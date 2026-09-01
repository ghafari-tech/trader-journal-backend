from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import *
from .models import Transaction
from app_portfolio.models import Portfolio
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from .mt5_bridge import connect_and_fetch_account
from .permissions import HasInternalSecret
from .serializers import MT5VerifyInternalSerializer

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