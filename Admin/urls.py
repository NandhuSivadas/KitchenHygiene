from django.urls import path,include
from Admin import views
app_name="webadmin"


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('view_hotels/', views.view_hotels, name='view_hotels'),
    path('add_hotel/', views.add_hotel, name='add_hotel'),
    path('upload_image/<int:hotel_id>/', views.admin_upload_image,name='admin_upload_image'),
    path('generate_certificate/<int:hotel_id>/', views.generate_certificate, name='generate_certificate'),
    path('view_report/<int:hotel_id>/', views.view_report_pdf, name='view_report_pdf'),
    path('download_report/<int:hotel_id>/', views.download_report_pdf, name='download_report_pdf'),
    path('reports/', views.view_reports, name='view_reports'),
    path('analyze_frame/', views.analyze_frame, name='analyze_frame'),
    path('approval_requests/', views.approval_requests, name='approval_requests'),
    path('update_verification/<int:hotel_id>/<str:action>/', views.update_verification, name='update_verification'),
    path('public-complaints/', views.view_public_complaints, name='view_public_complaints'),
    path('delete-public-complaint/<int:complaint_id>/', views.delete_public_complaint, name='delete_public_complaint'),
    path('export-complaints/', views.export_complaints, name='export_complaints'),


]
