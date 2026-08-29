from decimal import Decimal
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    TransactionDashboardSerializer,
    BestTransactionDashboardSerializer,
)
from drf_spectacular.utils import extend_schema
from app_transaction.models import Transaction

@extend_schema(tags=['Dashboard'])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    transactions = Transaction.objects.filter(
        user=request.user,
        exit_price__isnull=False,
    ).order_by("closed_at", "id")

    transactions_view = Transaction.objects.filter(
        user=request.user,
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