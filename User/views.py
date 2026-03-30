from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404


from User.models import *
from django.db.models import Sum, Avg



# ── helper ───────────────────────────────────────────────
def _require_hotel(request):
    hid = request.session.get("hid")
    if not hid:
        return None
    try:
        return tbl_hotel.objects.get(id=hid)
    except tbl_hotel.DoesNotExist:
        return None


# ── dashboard ────────────────────────────────────────────
def homepage(request):
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")

    # Calculate dynamic stats
    hotel_images = UploadModel.objects.filter(hotel=hotel).count()
    hotel_reviews = CustomerReview.objects.filter(hotel=hotel).count()
    hotel_certs = Certificate.objects.filter(hotel=hotel).count()
    
    # New Stats
    fines = HygieneViolation.objects.filter(hotel=hotel).aggregate(total=Sum('fine_amount'))['total'] or 0
    unseen_warnings = HotelWarning.objects.filter(hotel=hotel, is_read=False).count()

    ctx = {
        "user":          hotel,
        "hotel_images":  hotel_images,
        "hotel_reviews": hotel_reviews,
        "hotel_certs":   hotel_certs,
        "total_fines":   fines,
        "unseen_warnings": unseen_warnings,
    }
    return render(request, "User/Homepage.html", ctx)


# ── profile pages ────────────────────────────────────────
def myprofile(request):
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    return render(request, "User/MyProfile.html", {"user": hotel})


def editprofile(request):
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    
    if request.method == 'POST':
        hotel.hotel_name = request.POST['txt_name']
        hotel.hotel_email = request.POST['txt_email']
        hotel.hotel_contact = request.POST['txt_contact']
        hotel.hotel_address = request.POST['txt_address']
        hotel.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('webuser:myprofile')
    
    return render(request, 'User/editprofile.html', {'user': hotel})


def changepassword(request):
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")

    if request.method == "POST":
        current = request.POST.get("txt_currentpassword")
        new     = request.POST.get("txt_newpassword")
        confirm = request.POST.get("txt_confirmpassword")

        if current != hotel.hotel_password:
            messages.error(request, "Current password incorrect.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        else:
            hotel.hotel_password = new          # hash in prod
            hotel.save()
            messages.success(request, "Password changed.")
            return redirect("webuser:myprofile")

    return render(request, "User/ChangePassword.html", {"user": hotel})





# ── PDF Downloads ────────────────────────────────────────
def view_all_certificates(request):
    """View all certificates for the logged-in hotel"""
    from datetime import date
    
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    
    # Auto-expire certificates
    today = date.today()
    certificates = Certificate.objects.filter(hotel=hotel).order_by('-issue_date')
    
    for cert in certificates:
        if cert.valid_till < today and cert.status != 'Expired':
            cert.status = 'Expired'
            cert.save()
            
    # Fetch warnings for the Warnings tab
    ai_violations = HygieneViolation.objects.filter(hotel=hotel).order_by('-issue_date')
    hotel_warnings = list(HotelWarning.objects.filter(hotel=hotel).order_by('-created_at'))
    
    for warn in hotel_warnings:
        warn.photo_url = None
        warn.video_url = None
        if warn.complaint and warn.complaint.image:
            warn.photo_url = warn.complaint.image.url
        elif warn.complaint and warn.complaint.video:
            warn.video_url = warn.complaint.video.url
        else:
            upload = UploadModel.objects.filter(hotel=hotel, uploaded_at__lte=warn.created_at).order_by('-uploaded_at').first()
            if upload and upload.image:
                warn.photo_url = upload.image.url
            elif upload and upload.video:
                warn.video_url = upload.video.url
            
            
    return render(request, 'User/Certificates.html', {
        'certificates': certificates,
        'ai_violations': ai_violations,
        'hotel_warnings': hotel_warnings,
        'hotel': hotel
    })


def view_all_reports(request):
    """View all violation reports for the logged-in hotel"""
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    
    reports = HygieneViolation.objects.filter(hotel=hotel).order_by('-issue_date')
    return render(request, 'User/Reports.html', {'reports': reports, 'hotel': hotel})


def download_certificate(request, certificate_id):
    """Download certificate PDF"""
    from django.http import FileResponse, Http404
    import os
    
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    
    certificate = get_object_or_404(Certificate, id=certificate_id, hotel=hotel)
    
    if certificate.file and os.path.exists(certificate.file.path):
        response = FileResponse(open(certificate.file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Certificate_{certificate.certificate_number}.pdf"'
        return response
    else:
        messages.error(request, "Certificate file not found.")
        return redirect('webuser:view_all_certificates')


def download_report(request, report_id):
    """Download violation report PDF (legacy – serves stored pdf_file if present)"""
    from django.http import FileResponse
    import os

    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")

    report = get_object_or_404(HygieneViolation, id=report_id, hotel=hotel)

    if report.pdf_file and os.path.exists(report.pdf_file.path):
        response = FileResponse(open(report.pdf_file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Violation_Report_{report.id}.pdf"'
        return response
    else:
        # Fall back to preview page if no stored file
        return redirect('webuser:view_report', report_id=report_id)


def view_report(request, report_id):
    """Show a styled HTML preview of a violation report"""
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")

    report = get_object_or_404(HygieneViolation, id=report_id, hotel=hotel)
    return render(request, 'User/ViewReport.html', {
        'report': report,
        'hotel': hotel,
    })


def download_report_pdf(request, report_id):
    """Generate and download violation report as PDF from HTML template"""
    from django.http import HttpResponse
    from django.template.loader import get_template
    from io import BytesIO
    import xhtml2pdf.pisa as pisa

    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")

    report = get_object_or_404(HygieneViolation, id=report_id, hotel=hotel)

    template = get_template('User/ReportPDF.html')
    html_content = template.render({'report': report, 'hotel': hotel}, request)

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=buffer)

    if pisa_status.err:
        messages.error(request, "Failed to generate PDF. Please try again.")
        return redirect('webuser:view_report', report_id=report_id)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ViolationReport_{report.id}_{hotel.hotel_name}.pdf"'
    return response


def view_reviews(request):
    """View all guest reviews for the logged-in hotel"""
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    
    reviews = CustomerReview.objects.filter(hotel=hotel).order_by('-timestamp')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'User/Reviews.html', {
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count(),
        'hotel': hotel
    })



# ── logout ───────────────────────────────────────────────
def logout(request):
    """Clear session and redirect to login page"""
    request.session.flush()  # Clear all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect('guest:login')
