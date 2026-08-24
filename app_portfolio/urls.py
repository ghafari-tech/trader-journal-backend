from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('add/', views.portfolio_create, name='portfolio_add'),
    path('portfolio/<int:pk>/edit/', views.portfolio_edit, name='portfolio-edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio-delete'),
]