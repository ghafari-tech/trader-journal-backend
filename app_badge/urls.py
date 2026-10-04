from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.badge_list),
    path('titles/', views.badge_titles),
    path('my/', views.my_badges),
    path('add/', views.add_badge),
]