from django.urls import path
from app_setting import views

app_name = "settings"

urlpatterns = [
    path('user/', views.user_info, name='user_info'),
    path('plan/', views.user_plan_info, name='user_plan_info'),
    path('mt-connector/', views.metatrader_connect, name='metatrader_connect'),
    path('mt-status/', views.metatrader_status, name='metatrader_status'),
]