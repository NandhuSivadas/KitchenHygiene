# Admin/views.py
from Admin.models import tbl_admin
from User.models  import *
from django.shortcuts import render, redirect
from django.contrib import messages
from .yolov8_predict import check_hygiene
from django.shortcuts import render, redirect, get_object_or_404
from Admin.yolov8_predict import check_hygiene
from django.contrib import messages
from datetime import datetime, timedelta

def dashboard(request):
    return render(request,'Admin/Dashboard.html')

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
    hotels = tbl_hotel.objects.all()
    return render(request, 'Admin/ViewHotels.html', {'hotels': hotels})



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
            # ✅ Save image
            instance = UploadModel.objects.create(hotel=hotel, image=image_file)
            # ✅ Run prediction
            status, all_labels, violations = check_hygiene(instance.image.path)
            
        elif video_file:
            # ✅ Save video
            instance = UploadModel.objects.create(hotel=hotel, video=video_file)
            is_video = True
            video_path = instance.video.path
            
            # ✅ Run video prediction
            from .yolov8_predict import check_video_hygiene
            status, all_labels, violations = check_video_hygiene(video_path)

        if instance:
            # ✅ Update hygiene status of the hotel
            hotel.hygiene_status = status
            hotel.save()

            context.update({
                'image': instance.image.url if instance.image else None,
                'video': instance.video.url if instance.video else None,
                'is_video': is_video,
                'status': status,
                'violations': violations
            })

            # Optional: redirect back after success
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



def generate_certificate(request, hotel_id):
    hotel = get_object_or_404(tbl_hotel, id=hotel_id)
    image_obj = UploadModel.objects.filter(hotel=hotel).order_by('-uploaded_at').first()
    image_path = image_obj.image.path if image_obj else None

    # Create file path and name
    pdf_name = f"{hotel.hotel_name}_{hotel.hygiene_status}_Report.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, "violation_reports" if hotel.hygiene_status != "Clean" else "", pdf_name)

    # Ensure directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Generate PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 770, "Kitchen Hygiene Report")

    c.setFont("Helvetica", 14)
    c.drawString(100, 730, f"Hotel: {hotel.hotel_name}")
    c.drawString(100, 710, f"Address: {hotel.hotel_address}")
    c.drawString(100, 690, f"Hygiene Status: {hotel.hygiene_status}")
    c.drawString(100, 670, f"Issued on: {datetime.today().strftime('%Y-%m-%d')}")

    if hotel.hygiene_status == "Clean":
        # Generate clean certificate
        Certificate.objects.create(
            hotel=hotel,
            valid_till=datetime.today() + timedelta(days=365)
        )
        hotel.certificate_generated = True
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0, 0.6, 0)
        c.drawString(100, 640, "✅ Certified Clean! This kitchen meets hygiene standards.")
        c.setFillColorRGB(0, 0, 0)
    else:
        # Warning for dirty or moderate
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(1, 0, 0)
        c.drawString(100, 640, "⚠️ Hygiene Violation Detected!")
        c.setFont("Helvetica", 14)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(100, 620, "Please review and improve hygiene practices.")

        # Add image
        if image_path and os.path.exists(image_path):
            try:
                img = ImageReader(image_path)
                c.drawImage(img, 100, 380, width=300, height=200)
                c.drawString(100, 360, "Submitted Evidence:")
            except:
                c.drawString(100, 360, "⚠️ Image could not be displayed.")

        # Save violation record
        HygieneViolation.objects.create(
            hotel=hotel,
            hygiene_status=hotel.hygiene_status,
            pdf_file=f"violation_reports/{pdf_name}"  # path relative to MEDIA
        )

    c.setFont("Helvetica", 12)
    c.drawString(100, 150, "Issued by: Kitchen Hygiene Monitoring System")
    c.showPage()
    c.save()

    hotel.save()
    
    # Notify user
    messages.success(request, f"Certificate/Report for {hotel.hotel_name} has been generated and sent successfully.")
    
    # Redirect back to hotel list or dashboard
    return redirect('webadmin:view_hotels')

def view_reports(request):
    status = request.GET.get('status')
    if status and status != 'All':
        hotels = tbl_hotel.objects.filter(hygiene_status=status)
    else:
        hotels = tbl_hotel.objects.all()
    
    return render(request, 'Admin/Reports.html', {'hotels': hotels, 'current_status': status})

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
                
        # Run prediction
        try:
            status, labels, violations = check_hygiene(temp_path)
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
