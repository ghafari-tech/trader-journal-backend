from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('archive/', views.portfolio_archive_list, name='archive_list'),
    path('add/', views.portfolio_create, name='portfolio_add'),
    path('portfolio/<int:pk>/edit/', views.portfolio_edit, name='portfolio-edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio-delete'),
    path('portfolio/<int:pk>/archive/', views.portfolio_archive, name='portfolio-archive'),
    path('portfolio/<int:pk>/active/', views.active_portfolio, name='portfolio-active'),
]