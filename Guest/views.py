from django.shortcuts import render, redirect
import re
from django.contrib import messages
from User.models import *   # hotel table
from Admin.models import *
from Admin.yolov8_predict import check_hygiene, check_video_hygiene
from django.shortcuts import get_object_or_404

def homepage(request):
    return render(request, 'Guest/index.html')


# ── login ────────────────────────────────────────────────
def login(request):
    if request.method=="POST":
        email=request.POST.get("txt_email")
        password=request.POST.get("txt_password")

        if not email or not password:
            messages.error(request, "Please enter both email and password")
            return render(request,'Guest/login.html')
            
        hotelcount=tbl_hotel.objects.filter(hotel_email=email,hotel_password=password).count()
        admincount=tbl_admin.objects.filter(admin_email=email,admin_password=password).count()

        if hotelcount > 0:
            userdata=tbl_hotel.objects.get(hotel_email=email,hotel_password=password)
            
            # Check verification status
            if userdata.is_verified == 0:
                messages.warning(request, "Your account is pending admin approval. Please wait for verification.")
                return render(request,'Guest/login.html')
            elif userdata.is_verified == 2:
                messages.error(request, "Your account has been rejected by admin. Please contact support.")
                return render(request,'Guest/login.html')
            elif userdata.is_verified == 1:
                # Verified - allow login
                request.session['hid']=userdata.id
                return redirect('webuser:homepage')
                
        elif admincount > 0:
            admindata=tbl_admin.objects.get(admin_email=email,admin_password=password)
            request.session['aid']=admindata.id
            return redirect('webadmin:dashboard')
        else:
            messages.error(request, "Invalid credentials!")
            return render(request,'Guest/login.html')
    else:
        return render(request,'Guest/login.html')

    

def register_hotel(request):
    if request.method == "POST":
        name = request.POST.get("hotel_name")
        email = request.POST.get("hotel_email")
        password = request.POST.get("hotel_password")
        contact = request.POST.get("hotel_contact")
        address = request.POST.get("hotel_address")

        # Server-side Validation logic
        if not all([name, email, password, contact, address]):
             messages.error(request, "All fields are required.")
             return render(request, "Guest/register.html")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
             messages.error(request, "Invalid email address.")
             return render(request, "Guest/register.html")

        if len(password) < 6:
             messages.error(request, "Password must be at least 6 characters.")
             return render(request, "Guest/register.html")

        if not re.match(r"^\d{10}$", contact):
             messages.error(request, "Contact number must be 10 digits.")
             return render(request, "Guest/register.html")

        if tbl_hotel.objects.filter(hotel_email=email).exists():
             messages.error(request, "Email is already registered.")
             return render(request, "Guest/register.html")

        tbl_hotel.objects.create(
            hotel_name=name,
            hotel_email=email,
            hotel_password=password,
            hotel_contact=contact,
            hotel_address=address,
            is_verified=0  # Set to pending by default
        )

        messages.success(request, "Registration successful! Please wait for admin approval before logging in.")
        return redirect('guest:login')

    return render(request, "Guest/register.html")


def report_violation(request):
    if request.method == "POST":
        hotel_id = request.POST.get('hotel_id')
        description = request.POST.get('description')
        uploaded_file = request.FILES.get('file')
        
        hotel = get_object_or_404(tbl_hotel, id=hotel_id)
        
        # Determine if Video
        is_video = False
        if uploaded_file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            is_video = True
            
        # Save initially
        if is_video:
            complaint = PublicComplaint.objects.create(
                hotel=hotel,
                video=uploaded_file,
                description=description
            )
            file_path = complaint.video.path
        else:
            complaint = PublicComplaint.objects.create(
                hotel=hotel,
                image=uploaded_file,
                description=description
            )
            file_path = complaint.image.path
            
        # Run AI Analysis
        try:
            if is_video:
                status, _, _ = check_video_hygiene(file_path)
            else:
                status, _, _ = check_hygiene(file_path)
            
            # Update status
            complaint.ai_status = status
            if status in ['Dirty', 'Moderately Clean']:
                complaint.priority = 'High'
            else:
                complaint.priority = 'Low'
            complaint.save()
            
            msg = f"Report submitted! AI Analysis: {status}."
            if status == 'Dirty':
                msg += " High priority alert sent to Admin."
            messages.success(request, msg)
            
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            messages.warning(request, "Report submitted! Admin will review details manually.")
            
        return redirect('guest:report_violation')

    hotels = tbl_hotel.objects.filter(is_verified=1)
    return render(request, "Guest/ReportViolation.html", {'hotels': hotels})
