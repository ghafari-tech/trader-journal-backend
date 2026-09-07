import jdatetime
from datetime import datetime, time
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app_portfolio.views import portfolio_archive
from .serializers import *
from .models import Transaction
from app_portfolio.models import Portfolio
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from .mt5_bridge import connect_and_fetch_account
from .permissions import HasInternalSecret
from .serializers import MT5VerifyInternalSerializer
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from rest_framework.response import Response

@extend_schema(
    tags=["Transaction"],
    parameters=[
        OpenApiParameter(
            name="portfolio_id",
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description="ID of the portfolio",
        ),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    portfolio_id = request.query_params.get("portfolio_id")

    if not portfolio_id:
        return Response(
            {"detail": "portfolio_id is required."},
            status=400
        )
    
    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if portfolio.user != request.user:
        return Response({
            "detail": "portfolio id unavailable for user"
        }, status=403)

    transactions = Transaction.objects.filter(
        portfolio=portfolio,
    )

    serializer = TransactionSerializer(transactions, many=True)

    return Response({
        'transactions': serializer.data,
    }, status=200)


@extend_schema(tags=["Transaction"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_calendar(request):
    today = jdatetime.date.today()
    first_day_jalali = jdatetime.date(
        today.year,
        today.month,
        1
    )
    if today.month == 12:
        next_month_jalali = jdatetime.date(
            today.year + 1,
            1,
            1
        )
    else:
        next_month_jalali = jdatetime.date(
            today.year,
            today.month + 1,
            1
        )



    first_day_gregorian = first_day_jalali.togregorian()
    next_month_gregorian = next_month_jalali.togregorian()

    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True,
    ).first()

    transactions = (
        Transaction.objects
        .filter(
            portfolio=portfolio,
            created_at__gte=first_day_gregorian,
            created_at__lt=next_month_gregorian
        )
        .annotate(
            day=TruncDate('created_at')
        )
        .values('day')
        .annotate(
            transactions_count=Count('id'),
            profit_loss=Sum('profit_loss')
        )
        .order_by('day')
    )

    transactions_by_day = {
        item['day']: item
        for item in transactions
    }

    data = []

    current_day = first_day_jalali

    total_month = sum(
        item["profit_loss"] or 0
        for item in transactions
    )

    profitable_days = sum(
        1 for item in transactions
        if (item["profit_loss"] or 0) > 0
    )

    loss_days = sum(
        1 for item in transactions
        if (item["profit_loss"] or 0) < 0
    )

    best_day = max(
        transactions,
        key=lambda item: item["profit_loss"] or 0,
        default=None
    )

    while current_day < next_month_jalali:
        gregorian_day = current_day.togregorian()

        transaction_data = transactions_by_day.get(
            gregorian_day
        )

        data.append({
            "date": current_day.strftime("%Y/%m/%d"),
            "transactions_count": (
                transaction_data["transactions_count"]
                if transaction_data else 0
            ),
            "profit_loss": (
                float(transaction_data["profit_loss"])
                if transaction_data and transaction_data["profit_loss"] is not None
                else 0
            )
        })

        current_day += jdatetime.timedelta(days=1)

    return Response({
        "total_month": total_month,
        "profitable_days": profitable_days,
        "loss_days": loss_days,
        "best_day": best_day["profit_loss"] if best_day else 0,
        "calendar": data
    })


@extend_schema(tags=['MetaTrader'], request=MT5VerifyInternalSerializer)
@api_view(['POST'])
@permission_classes([HasInternalSecret])
def mt5_verify_internal(request):
    serializer = MT5VerifyInternalSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    result = connect_and_fetch_account(
        account_number=data['account_number'],
        investor_password=data['investor_password'],
        server=data['server'],
    )
    return Response(result, status=200)