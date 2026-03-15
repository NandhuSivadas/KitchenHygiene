# from django.db import models

# # Create your models here.
from django.db import models

class tbl_hotel(models.Model):
    hotel_name = models.CharField(max_length=100)
    hotel_email = models.EmailField(unique=True)
    hotel_password = models.CharField(max_length=128)
    hotel_contact = models.CharField(max_length=20, blank=True)
    hotel_address = models.CharField(max_length=255, blank=True)

    # Admin Verification Status
    is_verified = models.IntegerField(
        choices=[
            (0, 'Not Verified'),
            (1, 'Verified'),
            (2, 'Rejected')
        ],
        default=0
    )

    # Hygiene Prediction Result
    hygiene_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Clean', 'Clean'),
            ('Moderately Clean', 'Moderately Clean'),
            ('Dirty', 'Dirty'),
        ],
        default='Pending'
    )

    certificate_generated = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.hotel_name

class KitchenImage(models.Model):
    hotel        = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    image        = models.ImageField(upload_to="kitchens/")
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    ai_score     = models.FloatField(null=True, blank=True)
    ai_rating    = models.IntegerField(null=True, blank=True)




class CustomerReview(models.Model):
    hotel      = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, default="Anonymous Guest", blank=True)
    rating     = models.PositiveSmallIntegerField()
    review     = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)


class Certificate(models.Model):
    hotel       = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    issue_date  = models.DateField(auto_now_add=True)
    valid_till  = models.DateField()
    status      = models.CharField(max_length=20, default="Active")
    file        = models.FileField(upload_to='certificates/', null=True, blank=True)
    certificate_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.status}"

# User/models.py


class UploadModel(models.Model):
    hotel = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    video = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    hygiene_status = models.CharField(max_length=50, default="Pending")  # Clean, Dirty, Moderately Clean

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.image.name}"
    

class HygieneViolation(models.Model):
    hotel = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    hygiene_status = models.CharField(max_length=50)  # "Dirty" or "Moderately Clean"
    complaint = models.ForeignKey('PublicComplaint', on_delete=models.CASCADE, null=True, blank=True)
    pdf_file = models.FileField(upload_to='violation_reports/', null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.hygiene_status}"

class PublicComplaint(models.Model):
    hotel = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='public_complaints/images/', null=True, blank=True)
    video = models.FileField(upload_to='public_complaints/videos/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    # AI Analysis
    ai_status = models.CharField(max_length=50, default="Pending") # Clean/Dirty/Moderately Clean
    priority = models.CharField(max_length=20, default="Low") # High if Dirty
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Complaint against {self.hotel.hotel_name} - {self.priority}"

class HotelWarning(models.Model):
    hotel = models.ForeignKey(tbl_hotel, on_delete=models.CASCADE)
    complaint = models.ForeignKey(PublicComplaint, on_delete=models.CASCADE, null=True, blank=True)
    violation = models.ForeignKey(HygieneViolation, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Warning to {self.hotel.hotel_name} - {self.created_at}"