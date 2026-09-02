from drf_spectacular.utils import extend_schema, OpenApiParameter
from app_transaction.authentication import MetaTraderApiKeyAuthentication
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app_transaction.models import MetaTraderAccount
from .serializers import MetaTraderConnectSerializer



@extend_schema(tags=['Settings'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserInfoSerializer(request.user)
    return Response(serializer.data)

@extend_schema(tags=['Settings'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_plan_info(request):
    plan = Subscription.objects.filter(user=request.user).first()

    if not plan:
        plan = Subscription.objects.create(user=request.user)

    serializer = UserPlanSerializer(plan)

    return Response({
        'plan': serializer.data,
    })

@extend_schema(tags=['MetaTrader'], request=MetaTraderConnectSerializer)
@api_view(['POST'])
@authentication_classes([MetaTraderApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def metatrader_connect(request):
    account = request.auth  # از api_key پیدا شده

    serializer = MetaTraderConnectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    account.platform = data['platform']
    account.server = data['server']
    account.account_number = data['account_number']
    account.is_connected = True
    account.save()

    return Response({'status': 'connected'}, status=200)


@extend_schema(tags=['MetaTrader'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metatrader_status(request):
    account, _ = MetaTraderAccount.objects.get_or_create(user=request.user)
    return Response({
        'connected': account.is_connected,
        'platform': account.platform,
        'server': account.server,
        'account_number': account.account_number,
        'api_key': account.api_key,  # کاربر این رو کپی می‌کنه توی اکسپرت
    }, status=200)