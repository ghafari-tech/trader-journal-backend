import jdatetime
from drf_spectacular.utils import extend_schema, OpenApiRequest
from .serializers import *
from .models import Transaction
from app_portfolio.models import Portfolio
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from rest_framework.response import Response
from .pagination import TransactionPagination
from rest_framework import status
from app_transaction.models import MetaTraderAccount
from bs4 import BeautifulSoup
import re
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser


@extend_schema(tags=["Transaction"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not portfolio:
        return Response({
            'detail': 'No portfolio found',
        }, status=404)

    transactions = Transaction.objects.filter(
        portfolio=portfolio,
    ).order_by('-created_at')

    paginator = TransactionPagination()

    paginated_transactions = paginator.paginate_queryset(
        transactions,
        request
    )

    serializer = TransactionSerializer(
        paginated_transactions,
        many=True
    )

    return paginator.get_paginated_response({
        "transactions": serializer.data
    })


@extend_schema(tags=["Transaction"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_calendar(request, year, month):
    try:
        if not 1 <= month <= 12:
            return Response(
                {"detail": "ماه باید بین 1 تا 12 باشد."},
                status=400
            )

        first_day_jalali = jdatetime.date(
            year,
            month,
            1
        )

    except (ValueError, TypeError):
        return Response(
            {"detail": "سال یا ماه نامعتبر است."},
            status=400
        )

    if month == 12:
        next_month_jalali = jdatetime.date(
            year + 1,
            1,
            1
        )
    else:
        next_month_jalali = jdatetime.date(
            year,
            month + 1,
            1
        )

    first_day_gregorian = first_day_jalali.togregorian()
    next_month_gregorian = next_month_jalali.togregorian()

    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True,
    ).first()

    transactions = list(
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

    total_month = sum(
        item["profit_loss"] or 0
        for item in transactions
    )

    profitable_days = sum(
        1
        for item in transactions
        if (item["profit_loss"] or 0) > 0
    )

    loss_days = sum(
        1
        for item in transactions
        if (item["profit_loss"] or 0) < 0
    )

    best_day = max(
        transactions,
        key=lambda item: item["profit_loss"] or 0,
        default=None
    )

    data = []

    current_day = first_day_jalali
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
                if transaction_data
                and transaction_data["profit_loss"] is not None
                else 0
            )
        })

        current_day += jdatetime.timedelta(days=1)

    return Response({
        "year": year,
        "month": month,
        "total_month": float(total_month),
        "profitable_days": profitable_days,
        "loss_days": loss_days,
        "best_day": (
            float(best_day["profit_loss"])
            if best_day else 0
        ),
        "calendar": data
    })

@extend_schema(
    tags=["Transaction"],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "portfolio_id": {
                    "type": "integer",
                },
                "file": {
                    "type": "string",
                    "format": "binary",
                },
            },
            "required": [
                "portfolio_id",
                "file",
            ],
        }
    },
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def import_metatrader_report(request):
    serializer = ImportMetaTraderReportSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    portfolio_id = serializer.validated_data["portfolio_id"]
    uploaded_file = serializer.validated_data["file"]

    try:
        portfolio = Portfolio.objects.get(
            id=portfolio_id,
            user=request.user,
            is_archived=False
        )
    except Portfolio.DoesNotExist:
        return Response(
            {
                "detail": "Portfolio not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    file_content = uploaded_file.read()

    html_content = file_content.decode("utf-8")

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    positions_title = soup.find(
        lambda tag:
        tag.name == "div"
        and tag.get_text(strip=True) == "Positions"
    )

    if not positions_title:
        return Response(
            {
                "detail": "Positions section not found in report."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    positions_row = positions_title.find_parent("tr")

    header_row = positions_row.find_next_sibling("tr")

    current_row = header_row.find_next_sibling("tr")

    transactions = []

    date_pattern = re.compile(
        r"^\d{4}\.\d{2}\.\d{2} "
        r"\d{2}:\d{2}:\d{2}$"
    )

    while current_row:
        row_text = current_row.get_text(
            " ",
            strip=True
        )

        if row_text == "Orders":
            break

        cells = current_row.find_all("td")

        if (
            len(cells) >= 14
            and date_pattern.match(
                cells[0].get_text(strip=True)
            )
        ):
            transaction = {
                "open_time": cells[0].get_text(strip=True),
                "mt_ticket": cells[1].get_text(strip=True),
                "symbol": cells[2].get_text(strip=True),
                "transaction_type": cells[3].get_text(strip=True).lower(),
                "volume": cells[5].get_text(strip=True),
                "entry_price": cells[6].get_text(strip=True),
                "stop_loss": cells[7].get_text(strip=True),
                "take_profit": cells[8].get_text(strip=True),
                "closed_at": cells[9].get_text(strip=True),
                "exit_price": cells[10].get_text(strip=True),
                "commission": cells[11].get_text(strip=True),
                "swap": cells[12].get_text(strip=True),
                "profit_loss": cells[13].get_text(strip=True),
            }

            transactions.append(transaction)

        current_row = current_row.find_next_sibling("tr")

    for item in transactions:
        closed_at = None

        if item["closed_at"]:
            closed_at = datetime.strptime(
                item["closed_at"],
                "%Y.%m.%d %H:%M:%S"
            )

            closed_at = timezone.make_aware(
                closed_at
            )

        Transaction.objects.create(
            portfolio=portfolio,
            mt_ticket=item["mt_ticket"],
            symbol=item["symbol"],
            transaction_type=item["transaction_type"],
            entry_price=Decimal(item["entry_price"]),
            exit_price=(
                Decimal(item["exit_price"])
                if item["exit_price"]
                else None
            ),
            volume=Decimal(item["volume"]),
            stop_loss=(
                Decimal(item["stop_loss"])
                if item["stop_loss"]
                else None
            ),
            take_profit=(
                Decimal(item["take_profit"])
                if item["take_profit"]
                else None
            ),
            profit_loss=(
                Decimal(item["profit_loss"])
                if item["profit_loss"]
                else None
            ),
            closed_at=closed_at,
        )

    return Response(
        {
            "message": f"{len(transactions)} transactions imported successfully."
        },
        status=status.HTTP_200_OK
    )