from django.urls import path
from Guest import views

app_name = "guest"

urlpatterns = [
    
    path("",views.homepage,name="homepage"),
    path("login/",views.login,name="login"),
    path('register_hotel/', views.register_hotel,name='register_hotel'),
    path('report-violation/', views.report_violation, name='report_violation'),
    path('hotels/', views.view_hotels, name='view_hotels'),
    path('submit-review/', views.submit_review, name='submit_review'),

    
]
