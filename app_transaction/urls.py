from django.urls import path
from . import views

app_name = 'transaction'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('calendar/', views.transaction_calendar, name='transaction_calendar'),
]