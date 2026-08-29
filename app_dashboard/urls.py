from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('summery/', views.dashboard_summary, name='summery'),
    path("equity/", views.equity_chart, name='equity'),
]