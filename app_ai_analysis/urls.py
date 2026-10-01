from django.urls import path
from . import views

app_name = 'ai_analysis'

urlpatterns = [
    path('analysis/', views.ai_analysis_view, name='ai-analysis'),
]