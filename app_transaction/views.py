from django.db.models import Sum
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import Transaction
from app_portfolio.models import Portfolio

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