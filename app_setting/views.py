from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app_transaction.models import MetaTraderAccount
from .serializers import MetaTraderConnectSerializer
from app_transaction.utils import encrypt_password
from app_transaction.mt5_client import call_mt5_verify_service


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
@permission_classes([IsAuthenticated])
def metatrader_connect(request):
    serializer = MetaTraderConnectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if data['platform'] != 'mt5':
        return Response({'error': 'در حال حاضر فقط MT5 پشتیبانی می‌شود'}, status=400)

    result = call_mt5_verify_service(
        account_number=data['account_number'],
        investor_password=data['investor_password'],
        server=data['server'],
    )

    account, _ = MetaTraderAccount.objects.get_or_create(user=request.user)
    account.platform = data['platform']
    account.server = data['server']
    account.account_number = data['account_number']
    account.investor_password_encrypted = encrypt_password(data['investor_password'])
    account.is_connected = result.get('success', False)
    account.save()

    if not result.get('success'):
        return Response({'error': result.get('error', 'اتصال ناموفق بود')}, status=400)



@extend_schema(tags=['MetaTrader'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metatrader_status(request):
    try:
        account = request.user.mt_account
    except MetaTraderAccount.DoesNotExist:
        return Response({'connected': False}, status=200)

    return Response({
        'connected': account.is_connected,
        'platform': account.platform,
        'server': account.server,
        'account_number': account.account_number,
    }, status=200)