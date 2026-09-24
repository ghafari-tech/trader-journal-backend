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
        is_active=True,
        is_read=False
    )

    serializer = NotificationSerializer(notifications, many=True)

    return Response({
        'notifications': serializer.data,
    }, status=200)

@extend_schema(tags=['Notification'])
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def notification_click(request, pk):
    """با کلیک بر روی یکی از اعلانات این باید اجرا بشه"""
    notification = Notification.objects.get(pk=pk)

    if not notification:
        return Response({
            'message': 'Notification not found',
        }, status=404)

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return Response({
        'message': 'Notification reed',
    }, status=200)
