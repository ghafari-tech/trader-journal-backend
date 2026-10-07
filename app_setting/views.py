from drf_spectacular.utils import extend_schema
from django.utils import timezone
from app_notification.models import NotificationSettings
from app_portfolio.models import Portfolio
from app_setting.models import Subscription
from app_transaction.authentication import MetaTraderApiKeyAuthentication
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app_transaction.models import MetaTraderAccount
from .serializers import MetaTraderConnectSerializer
from decimal import Decimal
from app_transaction.models import Transaction
from django.db import transaction
import os
from django.conf import settings
from django.http import FileResponse



@extend_schema(tags=['Settings'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserInfoSerializer(request.user)
    return Response(serializer.data)

@extend_schema(tags=['Settings'], request=UpdateUserInfoSerializer)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    partial = request.method == 'PATCH'
    serializer = UpdateUserInfoSerializer(
        request.user,
        data=request.data,
        partial=partial,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(UserInfoSerializer(request.user).data, status=200)


@extend_schema(tags=['Settings'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_plan_info(request):
    plan = UserSubscription.objects.filter(user=request.user).first()

    if not plan:
        plan = UserSubscription.objects.create(user=request.user)

    serializer = UserPlanSerializer(plan)

    return Response({
        'plan': serializer.data,
    })

@extend_schema(tags=['MetaTrader'], request=MetaTraderConnectSerializer)
@api_view(['POST'])
@authentication_classes([MetaTraderApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def metatrader_connect(request):
    account = request.auth

    serializer = MetaTraderConnectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    account.platform = data['platform']
    account.server = data['server']
    account.account_number = data['account_number']
    account.last_seen = timezone.now()
    account.save()

    return Response({'status': 'connected'}, status=200)


@extend_schema(tags=['MetaTrader'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metatrader_status(request):
    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    account, _ = MetaTraderAccount.objects.get_or_create(
        portfolio=portfolio
    )

    return Response({
        'connected': account.connected,
        'platform': account.platform,
        'server': account.server,
        'account_number': account.account_number,
        'api_key': account.api_key,
        'last_seen': account.last_seen,
    })

@extend_schema(tags=['MetaTrader'])
@api_view(['POST'])
@authentication_classes([MetaTraderApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def metatrader_heartbeat(request):
    account = request.auth
    account.last_seen = timezone.now()

    account.save(update_fields=['last_seen'])

    return Response({
        'success': True,
        'connected': True
    })


@extend_schema(tags=['MetaTrader'])
@api_view(['POST'])
@authentication_classes([MetaTraderApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def metatrader_sync_transactions(request):

    account = request.auth

    transactions = request.data.get('transactions')

    if not isinstance(transactions, list):
        return Response({
            'success': False,
            'code': 'INVALID_TRANSACTIONS',
            'message': 'transactions must be a list.'
        }, status=400)

    created = 0
    updated = 0
    duplicated = 0

    with transaction.atomic():

        for item in transactions:

            ticket = str(item.get('mt_ticket', '')).strip()

            if not ticket:
                continue

            existing = Transaction.objects.filter(
                mt_ticket=ticket
            ).first()

            if existing:
                duplicated += 1

                existing.symbol = item.get(
                    'symbol',
                    existing.symbol
                )

                existing.volume = Decimal(
                    str(item.get(
                        'volume',
                        existing.volume
                    ))
                )

                if item.get('exit_price') is not None:
                    existing.exit_price = Decimal(
                        str(item['exit_price'])
                    )

                if item.get('profit_loss') is not None:
                    existing.profit_loss = Decimal(
                        str(item['profit_loss'])
                    )

                if item.get('stop_loss') is not None:
                    existing.stop_loss = Decimal(
                        str(item['stop_loss'])
                    )

                if item.get('take_profit') is not None:
                    existing.take_profit = Decimal(
                        str(item['take_profit'])
                    )

                if item.get('closed_at'):
                    existing.closed_at = item['closed_at']

                existing.save()

                updated += 1
                continue

            transaction_obj = Transaction.objects.create(
                portfolio=account.portfolio,

                mt_ticket=ticket,

                symbol=item['symbol'],

                transaction_type=item['transaction_type'],

                entry_price=Decimal(
                    str(item['entry_price'])
                ),

                exit_price=(
                    Decimal(str(item['exit_price']))
                    if item.get('exit_price') is not None
                    else None
                ),

                volume=Decimal(
                    str(item['volume'])
                ),

                profit_loss=(
                    Decimal(str(item['profit_loss']))
                    if item.get('profit_loss') is not None
                    else None
                ),

                stop_loss=(
                    Decimal(str(item['stop_loss']))
                    if item.get('stop_loss') is not None
                    else None
                ),

                take_profit=(
                    Decimal(str(item['take_profit']))
                    if item.get('take_profit') is not None
                    else None
                ),

                closed_at=item.get('closed_at')
            )

            created += 1

    account.last_seen = timezone.now()
    account.save(update_fields=['last_seen'])

    return Response({
        'success': True,
        'created': created,
        'updated': updated,
        'duplicated': duplicated
    })


@extend_schema(tags=['MetaTrader'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_ea(request):
    file_path = os.path.join(
        settings.BASE_DIR,
        'app_transaction',
        'static',
        'ea',
        'TradeJournalEA.ex5'
    )

    if not os.path.exists(file_path):
        return Response(
            {'detail': 'EA file not found.'},
            status=404
        )

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename='TradeJournalEA.ex5'
    )

@extend_schema(tags=['Settings'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    notification_settings, created = NotificationSettings.objects.get_or_create(
        user=request.user,
    )

    return Response({
        'add_journal_notif': notification_settings.add_journal_notif,
        'risk_up_warning_notif': notification_settings.risk_up_warning_notif,
        'ai_report_weekly_mail': notification_settings.ai_report_weekly_mail,
        'fomo_notif': notification_settings.fomo_notif,
    }, status=200)

@extend_schema(tags=["Settings"], request=UpdateNotificationSettingsSerializer)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_notification_setting(request):
    serializer = UpdateNotificationSettingsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    field = serializer.validated_data["field"]
    value = serializer.validated_data["value"]

    notification_settings, _ = NotificationSettings.objects.get_or_create(
        user=request.user,
    )

    setattr(notification_settings, field, value)
    notification_settings.save(update_fields=[field])

    return Response(
        {
            "message": "Notification setting updated successfully.",
            "field": field,
            "value": value,
        },status=200)


@extend_schema(tags=["Settings"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def plan_list(request):
    plans = Subscription.objects.all()

    serializers = PlanListSerializer(plans, many=True)

    return Response({
        "plans": serializers.data,
    }, status=200)