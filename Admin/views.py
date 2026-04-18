# Admin/views.py
from Admin.models import tbl_admin
from User.models  import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .ml_service import call_ml_predict_api
from datetime import datetime, timedelta
import re
import uuid
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.http import FileResponse, HttpResponse
def dashboard(request):
    # Counts for Stats Cards
    hotels_count = tbl_hotel.objects.count()
    clean_count = tbl_hotel.objects.filter(hygiene_status='Clean').count()
    dirty_count = tbl_hotel.objects.filter(hygiene_status='Dirty').count()
    pending_count = tbl_hotel.objects.filter(hygiene_status='Pending').count()
    ver_pending_count = tbl_hotel.objects.filter(is_verified=0).count()
    
    # Recent Activity (Last 5 registered hotels)
    recent_hotels = tbl_hotel.objects.all().order_by('-id')[:5]
    
    context = {
        'hotels_count': hotels_count,
        'clean_count': clean_count,
        'dirty_count': dirty_count,
        'pending_count': pending_count,
        'ver_pending_count': ver_pending_count,
        'recent_hotels': recent_hotels
    }
    return render(request, 'Admin/Dashboard.html', context)

# def upload_image(request):
#     context = {}

#     if request.method == "POST" and request.FILES.get("image"):
#         image = request.FILES['image']
#         instance = UploadModel.objects.create(image=image)
#         image_path = instance.image.path

#         status, all_labels, violations = check_hygiene(image_path)

#         context = {
#             'image': instance.image.url,
#             'status': status,
#             'violations': violations
#         }

#     return render(request, 'Admin/UploadImage.html', context)




def view_hotels(request):
    query = request.GET.get('q', '')
    if query:
        hotels = tbl_hotel.objects.filter(hotel_name__icontains=query)
    else:
        hotels = tbl_hotel.objects.all()
    return render(request, 'Admin/ViewHotels.html', {'hotels': hotels, 'search_query': query})

def add_hotel(request):
    if request.method == "POST":
        name = request.POST.get("hotel_name")
        email = request.POST.get("hotel_email")
        password = request.POST.get("hotel_password")
        contact = request.POST.get("hotel_contact")
        address = request.POST.get("hotel_address")

        if not all([name, email, password, contact, address]):
             messages.error(request, "All fields are required.")
             return render(request, "Admin/AddHotel.html")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
             messages.error(request, "Invalid email address.")
             return render(request, "Admin/AddHotel.html")

        if len(password) < 6:
             messages.error(request, "Password must be at least 6 characters.")
             return render(request, "Admin/AddHotel.html")

        if not re.match(r"^\d{10}$", contact):
             messages.error(request, "Contact number must be 10 digits.")
             return render(request, "Admin/AddHotel.html")

        if tbl_hotel.objects.filter(hotel_email=email).exists():
             messages.error(request, "Email is already registered.")
             return render(request, "Admin/AddHotel.html")

        tbl_hotel.objects.create(
            hotel_name=name,
            hotel_email=email,
            hotel_password=password,
            hotel_contact=contact,
            hotel_address=address,
            is_verified=1  # Verified since added by Admin
        )

        messages.success(request, "Hotel added successfully!")
        return redirect('webadmin:view_hotels')

    return render(request, "Admin/AddHotel.html")


def admin_upload_image(request, hotel_id):
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    context = {'hotel': hotel}

    if request.method == "POST":
        image_file = request.FILES.get("image")
        video_file = request.FILES.get("video")
        
        instance = None
        status = "Pending"
        violations = []
        is_video = False

        if image_file:
            instance = UploadModel.objects.create(hotel=hotel, image=image_file)
            status, violations = call_ml_predict_api(instance.image.path)
            
        elif video_file:
            instance = UploadModel.objects.create(hotel=hotel, video=video_file)
            is_video = True
            status, violations = call_ml_predict_api(instance.video.path, is_video=True)

        if instance:
            hotel.hygiene_status = status
            hotel.save()

            data = {
                'image': instance.image.url if instance.image else None,
                'video': instance.video.url if instance.video else None,
                'is_video': is_video,
                'status': status,
                'violations': violations,
                'hotel_id': hotel.id
            }

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse(data)

            context.update(data)
            messages.success(request, f"Hygiene status: {status}")
            return render(request, 'Admin/UploadImage.html', context)

    return render(request, 'Admin/UploadImage.html', context)





from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
import os





@xframe_options_sameorigin
def view_report_pdf(request, hotel_id):
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    pdf_name = f"{hotel.hotel_name}_{hotel.hygiene_status}_Report.pdf"
    
    if hotel.hygiene_status == "Clean":
        report_dir = settings.MEDIA_ROOT
    else:
        report_dir = os.path.join(settings.MEDIA_ROOT, "violation_reports")
        
    pdf_path = os.path.join(report_dir, pdf_name)
    
    if not os.path.exists(pdf_path):
        # Auto-generate if missing
        _generate_pdf_file(hotel)
        
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    else:
        return HttpResponse("Error generating Report PDF.", status=500)

def download_report_pdf(request, hotel_id):
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    pdf_name = f"{hotel.hotel_name}_{hotel.hygiene_status}_Report.pdf"
    
    if hotel.hygiene_status == "Clean":
        report_dir = settings.MEDIA_ROOT
    else:
        report_dir = os.path.join(settings.MEDIA_ROOT, "violation_reports")
        
    pdf_path = os.path.join(report_dir, pdf_name)
    
    if not os.path.exists(pdf_path):
        _generate_pdf_file(hotel)
        
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=pdf_name)
    else:
        messages.error(request, "Report PDF file not found to download.")
        return redirect('webadmin:view_reports')

def _generate_pdf_file(hotel):
    """Generates a premium PDF using xhtml2pdf and a template"""
    from django.template.loader import get_template
    from io import BytesIO
    import xhtml2pdf.pisa as pisa
    from User.models import HygieneViolation, UploadModel
    
    # Get last upload for evidence/status
    upload = UploadModel.objects.filter(hotel=hotel).order_by('-uploaded_at').first()
    status = hotel.hygiene_status
    
    if status == "Clean":
        template = get_template('User/CertificatePDF.html')
    else:
        template = get_template('User/ReportPDF.html')
    
    # Create a dummy report object if one doesn't exist yet for rendering
    # or fetch the most recent one
    report = HygieneViolation.objects.filter(hotel=hotel).order_by('-id').first()
    
    # Differentiate logic for Clean vs Dirty
    if status == "Clean":
        from User.models import Certificate
        # 1. Deactivate old active certificates
        Certificate.objects.filter(hotel=hotel, status="Active").update(status="Deactivated")
        
        # 2. Generate uniqe Cert Number
        cert_no = f"RMK-{hotel.id}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        # 3. Create fresh certificate record
        Certificate.objects.create(
            hotel=hotel,
            certificate_number=cert_no,
            valid_till=datetime.today() + timedelta(days=365)
        )
        hotel.certificate_generated = True
        hotel.save()
        
    pdf_name = f"{hotel.hotel_name}_{status}_Report.pdf"
    report_dir = settings.MEDIA_ROOT if status == "Clean" else os.path.join(settings.MEDIA_ROOT, "violation_reports")
    os.makedirs(report_dir, exist_ok=True)
    pdf_path = os.path.join(report_dir, pdf_name)

    # Render HTML to PDF
    context = {'report': report, 'hotel': hotel}
    if status == "Clean":
        from User.models import Certificate
        context['cert'] = Certificate.objects.filter(hotel=hotel).order_by('-id').first()
    html = template.render(context)
    
    with open(pdf_path, "wb") as f:
        if status == "Clean":
            # A4 Landscape: 297mm x 210mm in points (1pt = 1/72 inch, 1mm = 2.8346pt)
            # 297mm = 841.89pt, 210mm = 595.28pt
            pisa_status = pisa.CreatePDF(html, dest=f, pagesize=(841.89, 595.28))
        else:
            pisa_status = pisa.CreatePDF(html, dest=f)
    
    if pisa_status.err:
        return None
        
    if status != "Clean" and report:
        report.pdf_file = f"violation_reports/{pdf_name}"
        report.save()
        
    elif status == "Clean":
        from User.models import Certificate
        cert = Certificate.objects.filter(hotel=hotel).order_by('-id').first()
        if cert:
            cert.file = pdf_name
            cert.save()
        
    return pdf_path

def preview_warning(request, hotel_id=None, complaint_id=None):
    """Renders HTML preview for the admin modal, supporting both manual inspections and complaints"""
    from django.urls import reverse
    if complaint_id:
        complaint = get_object_or_404(PublicComplaint, id=complaint_id)
        hotel = complaint.hotel
        status = complaint.ai_status
        violations = [complaint.description] if complaint.description else ["Publicly reported hygiene violation"]
        target_url = reverse('webadmin:send_official_warning_complaint', kwargs={'complaint_id': complaint_id})
    else:
        hotel = get_object_or_404(tbl_hotel, id=hotel_id)
        status = hotel.hygiene_status
        violations = ["Kitchen surface contamination", "Improper waste disposal"] if status == "Dirty" else ["Minor cleaning required"]
        target_url = reverse('webadmin:send_official_warning', kwargs={'hotel_id': hotel_id})
    
    context = {
        'hotel': hotel,
        'status': status,
        'violations': violations,
        'complaint_id': complaint_id,
        'target_url': target_url,
        'current_time': datetime.now()
    }
    return render(request, 'Admin/WarningPreview.html', context)

def send_official_warning(request, hotel_id=None, complaint_id=None):
    """Final step: Create Violation, Generate PDF, and notify user"""
    if request.method == "POST":
        complaint = None
        if complaint_id:
            complaint = get_object_or_404(PublicComplaint, id=complaint_id)
            hotel = complaint.hotel
        else:
            hotel = get_object_or_404(tbl_hotel, id=hotel_id)
        
        # 1. Create the Violation Record
        fine_amount = request.POST.get('fine_amount', '0.00')
        if not fine_amount:
            fine_amount = '0.00'
            
        violation_obj = HygieneViolation.objects.create(
            hotel=hotel,
            hygiene_status=complaint.ai_status if complaint else hotel.hygiene_status,
            complaint=complaint,
            fine_amount=fine_amount
        )
        
        # 2. Generate the PDF
        _generate_pdf_file(hotel)
        
        # 3. Create a HotelWarning notification
        timestamp_str = datetime.now().strftime("%I:%M %p")
        custom_message = request.POST.get('custom_message', '').strip()
        
        if custom_message:
            msg = custom_message
        else:
            msg = f"Official Hygiene Warning Issued at {timestamp_str}. Status: {violation_obj.hygiene_status}. Please review the attached PDF report."
            if complaint:
                msg = f"Public Complaint Warning: {msg}"

        HotelWarning.objects.create(
            hotel=hotel,
            violation=violation_obj,
            complaint=complaint,
            message=msg,
            fine_amount=fine_amount
        )
        
        # Deactivate any active certificates
        from User.models import Certificate
        Certificate.objects.filter(hotel=hotel, status="Active").update(status="Deactivated")
        
        messages.success(request, f"Official warning and PDF report sent to {hotel.hotel_name} successfully.")
        
    if complaint_id:
        return redirect('webadmin:view_public_complaints')
    return redirect('webadmin:dashboard')

def generate_certificate(request, hotel_id):
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    _generate_pdf_file(hotel)
    
    messages.success(request, f"Certificate/Report for {hotel.hotel_name} has been generated and sent successfully.")
    return redirect('webadmin:view_hotels')



def view_reports(request):
    status = request.GET.get('status')
    query = request.GET.get('q', '')
    
    if status and status != 'All':
        hotels = tbl_hotel.objects.filter(hygiene_status=status)
    else:
        hotels = tbl_hotel.objects.exclude(hygiene_status='Pending')
        
    if query:
        hotels = hotels.filter(hotel_name__icontains=query)
    
    return render(request, 'Admin/Reports.html', {'hotels': hotels, 'current_status': status, 'search_query': query})

from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64
import uuid

def analyze_frame(request):
    if request.method == "POST" and request.FILES.get('frame'):
        frame_file = request.FILES['frame']
        
        # Save temp file for YOLO
        temp_filename = f"temp_frame_{uuid.uuid4()}.jpg"
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in frame_file.chunks():
                destination.write(chunk)
                
        # Run prediction via API
        try:
            status, violations = call_ml_predict_api(temp_path)
            labels = [] # Labels are now handled by the ML service
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return JsonResponse({'error': str(e)}, status=500)
            
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return JsonResponse({
            'status': status,
            'violations': violations,
            'labels': labels
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ── Approval Requests ────────────────────────────────────
def approval_requests(request):
    """Display all hotel registrations with pending approval status"""
    pending_hotels = tbl_hotel.objects.filter(is_verified=0).order_by('-id')
    all_hotels = tbl_hotel.objects.all().order_by('-id')
    
    # Get counts for stats
    pending_count = tbl_hotel.objects.filter(is_verified=0).count()
    approved_count = tbl_hotel.objects.filter(is_verified=1).count()
    rejected_count = tbl_hotel.objects.filter(is_verified=2).count()
    
    context = {
        'pending_hotels': pending_hotels,
        'all_hotels': all_hotels,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'Admin/ApprovalRequests.html', context)


def update_verification(request, hotel_id, action):
    """Approve or reject a hotel registration"""
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    
    if action == 'approve':
        hotel.is_verified = 1
        hotel.verified_at = datetime.now()
        hotel.save()
        messages.success(request, f"✅ {hotel.hotel_name} has been approved! They can now log in to their account.")
    elif action == 'reject':
        hotel.is_verified = 2
        hotel.save()
        messages.warning(request, f"❌ {hotel.hotel_name} has been rejected. They will not be able to log in.")
    
    return redirect('webadmin:approval_requests')

def view_public_complaints(request):
    complaints = PublicComplaint.objects.all().order_by('-submitted_at')
    
    # Filter by AI Status
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(ai_status=status_filter)
        
    # Filter by Priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
        
    context = {
        'complaints': complaints,
        'current_status': status_filter,
        'current_priority': priority_filter
    }
    return render(request, 'Admin/PublicComplaints.html', context)

def delete_public_complaint(request, complaint_id):
    complaint = get_object_or_404(PublicComplaint, id=complaint_id)
    complaint.delete()
    messages.success(request, "Complaint deleted successfully.")
    return redirect('webadmin:view_public_complaints')

import csv
from django.http import HttpResponse

def export_complaints(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="public_complaints.csv"'

    writer = csv.writer(response)
    writer.writerow(['Hotel Name', 'Date Submitted', 'AI Analysis Status', 'Priority', 'Description'])

    complaints = PublicComplaint.objects.all().order_by('-submitted_at')
    for complaint in complaints:
        writer.writerow([
            complaint.hotel.hotel_name if complaint.hotel else 'N/A',
            complaint.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if complaint.submitted_at else 'N/A',
            complaint.ai_status,
            complaint.priority,
            complaint.description
        ])

    return response

def send_warning(request, complaint_id):
    if request.method == "POST":
        complaint = get_object_or_404(PublicComplaint, id=complaint_id)
        message_text = request.POST.get("warning_message")
        
        if message_text:
            HotelWarning.objects.create(
                hotel=complaint.hotel,
                complaint=complaint,
                message=message_text
            )
            messages.success(request, f"Warning message sent to {complaint.hotel.hotel_name}.")
        else:
            messages.error(request, "Warning message cannot be empty.")
            
    return redirect('webadmin:view_public_complaints')
