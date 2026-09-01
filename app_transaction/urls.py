from django.urls import path
from . import views

app_name = 'transaction'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
path('internal/mt5-verify/', views.mt5_verify_internal, name='mt5_verify_internal'),
]