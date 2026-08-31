from django.urls import path
from app_setting import views

app_name = "settings"

urlpatterns = [
    path('user/', views.user_info, name='user_info'),
    path('plan/', views.user_plan_info, name='user_plan_info'),
]