from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from app_portfolio.models import Portfolio
from app_portfolio.views import portfolio_edit
from .serializers import (
    TransactionDashboardSerializer,
    BestTransactionDashboardSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app_transaction.models import Transaction
import jdatetime
from decimal import Decimal


@extend_schema(tags=['Dashboard'])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary(request):
    portfolios = Portfolio.objects.filter(
        user=request.user,
    )

    if not portfolios.exists():
        return Response(
            {"detail": "portfolio not found."},
            status=404
        )

    transactions = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
    ).order_by("closed_at", "id")

    transactions_view = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
    ).order_by("closed_at", "id")[:8]

    transaction_serializer = TransactionDashboardSerializer(
        transactions_view,
        many=True
    )

    best_transaction = None
    worst_transaction = None

    if transactions.exists():
        best_transaction = max(
            transactions,
            key=lambda transaction: transaction.profit_loss or Decimal("0")
        )

        worst_transaction = min(
            transactions,
            key=lambda transaction: transaction.profit_loss or Decimal("0")
        )

    best_transaction_serializer = (
        BestTransactionDashboardSerializer(best_transaction)
        if best_transaction
        else None
    )

    worst_transaction_serializer = (
        BestTransactionDashboardSerializer(worst_transaction)
        if worst_transaction
        else None
    )

    total_profit = sum(
        (
            transaction.profit_loss
            for transaction in transactions
            if transaction.profit_loss is not None
            and transaction.profit_loss > 0
        ),
        Decimal("0")
    )

    total_loss = sum(
        (
            abs(transaction.profit_loss)
            for transaction in transactions
            if transaction.profit_loss is not None
            and transaction.profit_loss < 0
        ),
        Decimal("0")
    )

    total_reward = sum(
        (
            transaction.profit_loss
            for transaction in transactions
            if transaction.profit_loss is not None
        ),
        Decimal("0")
    )

    total_trades = transactions.count()

    winning_trades = sum(
        1
        for transaction in transactions
        if transaction.profit_loss is not None
        and transaction.profit_loss > 0
    )

    losing_trades = sum(
        1
        for transaction in transactions
        if transaction.profit_loss is not None
        and transaction.profit_loss < 0
    )

    if total_trades > 0:
        win_rate = (
            Decimal(winning_trades)
            / Decimal(total_trades)
            * Decimal("100")
        )
    else:
        win_rate = Decimal("0")

    if total_loss > 0:
        profit_factor = total_profit / total_loss
    else:
        profit_factor = None

    equity = Decimal("0")
    peak = Decimal("0")
    max_drawdown = Decimal("0")

    for transaction in transactions:
        if transaction.profit_loss is None:
            continue
        equity += transaction.profit_loss
        if equity > peak:
            peak = equity

        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    return Response({
        "total_reward": total_reward,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
        "profit_factor": (
            round(profit_factor, 2)
            if profit_factor is not None
            else None
        ),
        "max_drawdown": max_drawdown,
        "best_transaction": (
            best_transaction_serializer.data
            if best_transaction_serializer
            else None
        ),
        "worst_transaction": (
            worst_transaction_serializer.data
            if worst_transaction_serializer
            else None
        ),
        "transactions": transaction_serializer.data,
    })

@extend_schema(tags=["Dashboard"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def equity_chart(request):
    portfolios = Portfolio.objects.filter(
        user=request.user
    )

    if not portfolios.exists():
        return Response(
            {"detail": "Portfolio not found."},
            status=404
        )

    today = timezone.localdate()
    start_date = today - timedelta(days=29)

    transactions = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
        closed_at__isnull=False,
        closed_at__date__gte=start_date,
        closed_at__date__lte=today,
    ).order_by("closed_at", "id")

    daily_profit_loss = {}

    for transaction in transactions:
        transaction_date = transaction.closed_at.date()
        daily_profit_loss.setdefault(
            transaction_date,
            Decimal("0")
        )
        daily_profit_loss[transaction_date] += (
            transaction.profit_loss or Decimal("0")
        )

    total_profit_loss = sum(
        daily_profit_loss.values(),
        Decimal("0")
    )

    total_balance = 0
    for portfolio in portfolios:
        total_balance += portfolio.balance

    starting_equity = (
        total_balance - total_profit_loss
    )

    equity = starting_equity
    data = []

    for i in range(30):
        current_date = start_date + timedelta(days=i)
        equity += daily_profit_loss.get(
            current_date,
            Decimal("0")
        )

        data.append({
            "date": current_date,
            "equity": equity,
        })

    return Response({
        "start_date": start_date,
        "end_date": today,
        "data": data,
    })

@extend_schema(tags=["Dashboard"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def win_loss_rate(request):
    portfolios = Portfolio.objects.filter(
        user=request.user
    )

    if not portfolios.exists():
        return Response(
            {"detail": "Portfolio not found."},
            status=404
        )

    transactions = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
    )

    total_trades = transactions.count()

    winning_trades = transactions.filter(
        profit_loss__gt=0
    ).count()

    losing_trades = transactions.filter(
        profit_loss__lt=0
    ).count()

    break_even_trades = transactions.filter(
        profit_loss=0
    ).count()

    if total_trades == 0:
        return Response({
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "break_even_trades": 0,
            "win_rate": 0,
            "loss_rate": 0,
        })

    win_rate = (winning_trades / total_trades) * 100
    loss_rate = (losing_trades / total_trades) * 100

    return Response({
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "break_even_trades": break_even_trades,
        "win_rate": round(win_rate, 2),
        "loss_rate": round(loss_rate, 2),
    })

@extend_schema(tags=["Dashboard"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_performance(request):
    months = [
        "فروردین", "اردیبهشت", "خرداد",
        "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر",
        "دی", "بهمن", "اسفند",
    ]

    portfolios = Portfolio.objects.filter(
        user=request.user
    )

    if not portfolios.exists():
        return Response(
            {"detail": "Portfolio not found."},
            status=404
        )

    transactions = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
    )

    now = timezone.localtime()
    today_jalali = jdatetime.date.fromgregorian(
        date=now.date()
    )

    current_year = today_jalali.year

    result = []

    for month in range(1, 13):
        start_jalali = jdatetime.date(
            current_year,
            month,
            1
        )

        if month == 12:
            next_month_jalali = jdatetime.date(
                current_year + 1,
                1,
                1
            )
        else:
            next_month_jalali = jdatetime.date(
                current_year,
                month + 1,
                1
            )

        start_date = start_jalali.togregorian()
        next_month_date = next_month_jalali.togregorian()

        monthly_transactions = transactions.filter(
            closed_at__gte=start_date,
            closed_at__lt=next_month_date,
        )

        profit = 0
        loss = 0

        for transaction in monthly_transactions:
            if transaction.profit_loss > 0:
                profit += transaction.profit_loss

            elif transaction.profit_loss < 0:
                loss += transaction.profit_loss

        result.append({
            "month": months[month - 1],
            "month_number": month,
            "profit": profit,
            "loss": loss,
            "net": profit + loss,
        })

    return Response({
        "year": current_year,
        "months": result,
    })


@extend_schema(tags=["Dashboard"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def drawdown(request):
    portfolios = Portfolio.objects.filter(
        user=request.user
    )

    transactions = Transaction.objects.filter(
        portfolio__in=portfolios,
        exit_price__isnull=False,
        profit_loss__isnull=False,
    ).order_by("closed_at")

    equity = Decimal("0")
    peak = Decimal("0")

    data = []

    for transaction in transactions:
        equity += transaction.profit_loss

        if equity > peak:
            peak = equity

        if peak == 0:
            dd = Decimal("0")
        else:
            dd = ((equity - peak) / peak) * 100

        data.append({
            "date": transaction.closed_at,
            "dd": round(dd, 2),
        })

    return Response(data)