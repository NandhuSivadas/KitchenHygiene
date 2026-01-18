from django.urls import path
from . import views

app_name = "webuser"

urlpatterns = [
    path("homepage/",views.homepage,name="homepage"),
    path("profile/",views.myprofile,name="myprofile"),
    path("edit-profile/",views.editprofile,name="editprofile"),
    path("change-password/",views.changepassword,name="changepassword"),
    path('logout/', views.logout, name='logout'),
    
    # PDF Downloads
    path('certificates/', views.view_all_certificates, name='view_all_certificates'),
    path('reports/', views.view_all_reports, name='view_all_reports'),
    path('download-certificate/<int:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('download-report/<int:report_id>/', views.download_report, name='download_report'),
  
]
