from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('add/', views.portfolio_create, name='portfolio_add'),
]