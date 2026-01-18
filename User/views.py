from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404


from User.models import *



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

    ctx = {
        "user":          hotel,
        "hotel_images":  KitchenImage.objects.filter(hotel=hotel).count(),
        "hotel_reviews": CustomerReview.objects.filter(hotel=hotel).count(),
        "hotel_certs":   Certificate.objects.filter(hotel=hotel).count(),
    }
    return render(request, "User/Homepage.html", ctx)


# ── profile pages ────────────────────────────────────────
def myprofile(request):
    hotel = _require_hotel(request)
    if not hotel:
        return redirect("guest:login")
    return render(request, "User/MyProfile.html", {"user": hotel})


def editprofile(request):
    user = request.user  # or fetch from session if you’re using a custom login
    
    if request.method == 'POST':
        user.hotel_name = request.POST['txt_name']
        user.hotel_email = request.POST['txt_email']
        user.hotel_contact = request.POST['txt_contact']
        user.hotel_address = request.POST['txt_address']
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('webuser:myprofile')
    
    return render(request, 'User/editprofile.html', {'user': user})


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
            
    return render(request, 'User/Certificates.html', {
        'certificates': certificates,
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
    """Download violation report PDF"""
    from django.http import FileResponse, Http404
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
        messages.error(request, "Report file not found.")
        return redirect('webuser:view_all_reports')


# ── logout ───────────────────────────────────────────────
def logout(request):
    """Clear session and redirect to login page"""
    request.session.flush()  # Clear all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect('guest:login')
