from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('summery/', views.summary, name='summery'),
    path("equity/", views.equity_chart, name='equity'),
    path("win-loss-rate/", views.win_loss_rate, name='win_loss_rate'),
    path("monthly-performance/", views.monthly_performance, name='monthly_performance'),
    path("drawdown/", views.drawdown, name='drawdown'),
]