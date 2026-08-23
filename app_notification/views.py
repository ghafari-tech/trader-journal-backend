from django.contrib.auth import authenticate
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from app_transaction.models import Transaction
from app_user.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from app_notification.models import Notification

@extend_schema(tags=['Notification'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_user_list(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_active=True
    )

    serializer = NotificationSerializer(notifications, many=True)

    return JsonResponse({
        'notifications': serializer.data,
    }, status=200)