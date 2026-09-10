from django.urls import path
from app_setting import views

urlpatterns = [
    path('user-info/', views.user_info, name='user_info'),
    path('plan/', views.user_plan_info, name='user_plan_info'),
    path('metatrader/connect/', views.metatrader_connect, name='metatrader_connect'),
    path('metatrader/heartbeat/', views.metatrader_heartbeat, name='metatrader_heartbeat'),
    path('metatrader/sync-transactions/', views.metatrader_sync_transactions, name='metatrader_sync_transactions'),
    path('metatrader/download-ea/', views.download_ea, name='download_ea'),
]
