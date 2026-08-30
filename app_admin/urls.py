from django.urls import path
from . import views

app_name = "admin"

urlpatterns = [
    path('users/', views.users_list, name='users_list'),
]