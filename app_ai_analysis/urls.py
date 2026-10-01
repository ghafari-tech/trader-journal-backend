from django.urls import path
from .views import *

urlpatterns = [
    path("", ai_analysis_view, name="ai-analysis"),
    path("regenerate/", regenerate_ai_analysis_view, name="ai-analysis-regenerate"),
    path("models/", ai_models_list_view, name="ai-models-list"),
]