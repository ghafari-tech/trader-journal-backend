from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from .serializers import *

@extend_schema(tags=['Risk Management'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def risk_management_show(request):
    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    risk_manage, created = RiskManagement.objects.get_or_create(
        portfolio=portfolio,
    )

    serializer = RiskManageSerializer(risk_manage)

    return Response({
        'riskmanage': serializer.data,
    }, status=200)

@extend_schema(tags=['Risk Management'], request=EditRiskManageSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_risk_management(request):
    max_risk = request.data.get('max_risk')
    max_loss_daily = request.data.get('max_loss_daily')
    max_loss_weekly = request.data.get('max_loss_weekly')
    max_transaction_daily = request.data.get('max_transaction_daily')
    max_consecutive_loss = request.data.get('max_consecutive_loss')
    min_r_r = request.data.get('min_r_r')

    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    risk_manage, created = RiskManagement.objects.get_or_create(
        portfolio=portfolio,
    )

    if max_risk != risk_manage.max_risk:
        risk_manage.max_risk = max_risk
    if max_loss_daily != risk_manage.max_loss_daily:
        risk_manage.max_loss_daily = max_loss_daily
    if max_loss_weekly != risk_manage.max_loss_weekly:
        risk_manage.max_loss_weekly = max_loss_weekly
    if max_transaction_daily != risk_manage.max_transaction_daily:
        risk_manage.max_transaction_daily = max_transaction_daily
    if max_consecutive_loss != risk_manage.max_consecutive_loss:
        risk_manage.max_consecutive_loss = max_consecutive_loss
    if min_r_r != risk_manage.min_r_r:
        risk_manage.min_r_r = min_r_r

    risk_manage.save()

    return Response({
        'message': 'Risk Management has been updated.',
    }, status=200)


@extend_schema(tags=["Risk Management"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def look_risk_management(request):
    portfolio = Portfolio.objects.filter(user=request.user, is_active=True).first()

    if not portfolio:
        return Response({"detail": "پرتفوی فعالی پیدا نشد."}, status=404)

    risk_management, _ = RiskManagement.objects.get_or_create(portfolio=portfolio)

    balance = Decimal(str(portfolio.balance))
    max_risk = Decimal(str(risk_management.max_risk))
    max_loss_daily = Decimal(str(risk_management.max_loss_daily))
    max_loss_weekly = Decimal(str(risk_management.max_loss_weekly))
    max_transaction_daily = Decimal(str(risk_management.max_transaction_daily))
    max_consecutive_loss_setting = Decimal(str(risk_management.max_consecutive_loss))
    min_r_r_setting = Decimal(str(risk_management.min_r_r))

    transaction = (
        Transaction.objects
        .filter(portfolio=portfolio, profit_loss__isnull=False, profit_loss__lt=0)
        .order_by("profit_loss")
        .first()
    )

    loss_amount = abs(transaction.profit_loss) if transaction else Decimal("0")
    risk_amount_in_trade = balance * (max_risk / Decimal("100"))

    if risk_amount_in_trade > 0:
        max_risk_in_trade = loss_amount / risk_amount_in_trade * Decimal("100")
    else:
        max_risk_in_trade = Decimal("0")

    today = timezone.localdate()

    transactions_in_day = Transaction.objects.filter(
        portfolio=portfolio,
        created_at__date=today,
        profit_loss__isnull=False,
    )

    loss_amount_in_day = sum(
        (abs(transaction.profit_loss) for transaction in transactions_in_day if transaction.profit_loss < 0),
        Decimal("0")
    )

    risk_amount_in_day = balance * (max_loss_daily / Decimal("100"))

    if risk_amount_in_day > 0:
        max_risk_in_day = loss_amount_in_day / risk_amount_in_day * Decimal("100")
    else:
        max_risk_in_day = Decimal("0")

    week_start = today
    week_end = today + timedelta(days=7)

    transactions_in_week = Transaction.objects.filter(
        portfolio=portfolio,
        created_at__date__gte=week_start,
        created_at__date__lt=week_end,
        profit_loss__isnull=False,
    )

    loss_amount_in_week = sum(
        (abs(transaction.profit_loss) for transaction in transactions_in_week if transaction.profit_loss < 0),
        Decimal("0")
    )

    risk_amount_in_week = balance * (max_loss_weekly / Decimal("100"))

    if risk_amount_in_week > 0:
        max_risk_in_week = loss_amount_in_week / risk_amount_in_week * Decimal("100")
    else:
        max_risk_in_week = Decimal("0")

    transactions_count_in_day = transactions_in_day.count()

    if max_transaction_daily > 0:
        max_transaction_in_day = Decimal(str(transactions_count_in_day)) / max_transaction_daily * Decimal("100")
    else:
        max_transaction_in_day = Decimal("0")

    transactions = (
        Transaction.objects
        .filter(portfolio=portfolio, profit_loss__isnull=False, closed_at__isnull=False)
        .order_by("-closed_at")
    )

    consecutive_loss = 0

    for transaction in transactions:
        if transaction.profit_loss < 0:
            consecutive_loss += 1
        else:
            break

    if max_consecutive_loss_setting > 0:
        max_consecutive_loss = Decimal(str(consecutive_loss)) / max_consecutive_loss_setting * Decimal("100")
    else:
        max_consecutive_loss = Decimal("0")

    transaction_min_r_r = (
        Transaction.objects
        .filter(portfolio=portfolio, r_r__isnull=False)
        .order_by("r_r")
        .first()
    )

    if transaction_min_r_r and min_r_r_setting > 0:
        min_r_r = transaction_min_r_r.r_r / min_r_r_setting * Decimal("100")
    else:
        min_r_r = Decimal("0")

    max_risk_in_trade = min(max_risk_in_trade, Decimal("100"))
    max_risk_in_day = min(max_risk_in_day, Decimal("100"))
    max_risk_in_week = min(max_risk_in_week, Decimal("100"))
    max_transaction_in_day = min(max_transaction_in_day, Decimal("100"))
    max_consecutive_loss = min(max_consecutive_loss, Decimal("100"))
    min_r_r = min(min_r_r, Decimal("100"))

    return Response({
        "max_risk_in_trade": max_risk_in_trade,
        "max_risk_in_day": max_risk_in_day,
        "max_risk_in_week": max_risk_in_week,
        "max_transaction_in_day": max_transaction_in_day,
        "max_consecutive_loss": max_consecutive_loss,
        "min_r_r": min_r_r,
    }, status=200)






