from django.urls import path
from . import views

app_name = "custom_admin"

urlpatterns = [
    path("", views.admin_main, name="main"),
    path('users/', views.users_list, name='users_list'),
    path('pays/', views.pays_list, name='pays_list'),
    path('subscriptions/', views.subscriptions_list, name='subscriptions_list'),
    path('subscriptions/update/<int:pk>/', views.update_subscription, name='subscriptions_update'),
    path('ai-models/', views.ai_models_list, name='ai_models_list'),
    path('ai-models/add/', views.ai_model_create, name='ai_model_create'),
]
