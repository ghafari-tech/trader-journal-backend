from django.urls import path
from app_goal import views

app_name = 'goal'

urlpatterns = [
    path('', views.goal_list, name='goals'),
    path('add/', views.add_goal, name='add'),
    path('edit/<int:pk>/', views.edit_goal, name='edit'),
    path('delete/<int:pk>/', views.delete_goal, name='delete'),
]