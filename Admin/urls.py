from django.urls import path,include
from Admin import views
app_name="webadmin"


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('view_hotels/', views.view_hotels, name='view_hotels'),
    path('upload_image/<int:hotel_id>/', views.admin_upload_image,name='admin_upload_image'),
    path('generate_certificate/<int:hotel_id>/', views.generate_certificate, name='generate_certificate'),
    path('reports/', views.view_reports, name='view_reports'),
    path('analyze_frame/', views.analyze_frame, name='analyze_frame'),


]
