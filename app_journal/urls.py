from django.urls import path
from . import views


urlpatterns = [
    path('', views.journal_list, name='journal_list'),
    path('add/', views.add_journal, name='add_journal'),
]