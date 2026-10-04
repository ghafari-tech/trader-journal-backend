from django.shortcuts import get_object_or_404

from app_setting.models import Subscription
from treider_project import settings
from .models import Api_Ai
from .serializers import *
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from app_user.models import User, UserSubscription


@extend_schema(tags=['Admin'])
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def users_list(request):
    users = User.objects.all()
    subscription_free = Subscription.objects.filter(name='Free').first()

    for user in users:
        if not hasattr(user, "plan"):
            UserSubscription.objects.create(user=user, type=subscription_free)

    serializer = UserAdminSerializer(users, many=True)

    return Response({
        'users': serializer.data
    }, status=200)

@extend_schema(tags=['Admin'])
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_main(request):
    users_count = User.objects.all().count()
    subscriptions_count = UserSubscription.objects.exclude(type=None).count()
    income_monthly = 0
    api_calls = 0

    return Response({
        'users_count': users_count,
        'subscriptions_count': subscriptions_count,
        'income_monthly': income_monthly,
        'api_calls': api_calls
    }, status=200)

@extend_schema(tags=['Admin'])
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def pays_list(request):
    return Response([], status=200)

@extend_schema(tags=['Admin'])
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def subscriptions_list(request):
    subscriptions = Subscription.objects.all()

    serializer = SubscriptionSerializer(subscriptions, many=True)

    return Response({
        'subscriptions': serializer.data,
    }, status=200)

@extend_schema(
    tags=["Admin"],
    request=SubscriptionSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_subscription(request, pk):
    subscription = get_object_or_404(
        Subscription,
        pk=pk
    )

    serializer = SubscriptionSerializer(
        subscription,
        data=request.data,
        partial=True
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        {
            "message": "Subscription updated successfully.",
            "subscription": serializer.data,
        },
        status=200
    )

@extend_schema(tags=["Admin"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def apis_list(request):
    apis = Api_Ai.objects.all()

    serializers = ApiSerializer(apis, many=True)

    return Response({
        'apis': serializers.data,
    })


