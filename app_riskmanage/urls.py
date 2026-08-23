from django.urls import path
from . import views

app_name = 'riskmanage'

urlpatterns = [
    path('', views.risk_management_show, name='risk_management_show'),
    path('update/', views.edit_risk_management, name='edit_risk_management'),
]