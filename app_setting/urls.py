from django.urls import path
from app_setting import views

app_name = "settings"

urlpatterns = [
    path('user/', views.user_info, name='user_info'),
    path('plan/', views.user_plan_info, name='user_plan_info'),
    path('mt-connector/', views.metatrader_connect, name='metatrader_connect'),
    path('mt-status/', views.metatrader_status, name='metatrader_status'),
    path('sync-transactions/', views.metatrader_sync_transactions, name='metatrader_sync_transactions'),
    path('heartbeat/', views.metatrader_heartbeat, name='metatrader_heartbeat'),
    path('metatrader/download-ea/', views.download_ea, name='download_ea'),
]