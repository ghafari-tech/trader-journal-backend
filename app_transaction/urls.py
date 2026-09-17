from django.urls import path
from . import views

app_name = 'transaction'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('trades/calendar/<int:year>/<int:month>/', views.transaction_calendar, name='transaction_calendar'),
    path('add/import/', views.import_metatrader_report, name='import_transactions'),
]