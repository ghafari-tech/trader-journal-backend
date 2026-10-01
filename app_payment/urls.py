from django.urls import path

from app_payment import views


urlpatterns = [
    path('request/', views.create_payment, name='payment-request'),
    path('verify/', views.verify_payment, name='payment-verify'),
]