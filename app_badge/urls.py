from django.urls import path
from . import views

app_name = 'badge'

urlpatterns = [
    path('', views.badge_list, name='badges'),
    path('add/', views.add_badge, name='add_badge'),
]