from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    path('', views.notification_user_list, name='notification_list'),
    path('read/<int:pk>/', views.notification_click, name='notification_read'),
]