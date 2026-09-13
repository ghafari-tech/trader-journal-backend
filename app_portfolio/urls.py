from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('archive/', views.portfolio_archive_list, name='archive_list'),
    path('add/', views.portfolio_create, name='portfolio_add'),
    path('edit/<int:pk>/', views.portfolio_edit, name='portfolio-edit'),
    path('delete/<int:pk>/', views.portfolio_delete, name='portfolio-delete'),
    path('archive/<int:pk>/', views.portfolio_archive, name='portfolio-archive'),
    path('archive-out/<int:pk>/', views.archive_out_portfolio, name='portfolio-archive-out'),
    path('active/<int:pk>/', views.active_portfolio, name='portfolio-active'),
]