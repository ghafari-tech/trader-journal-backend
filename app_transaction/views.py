from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import Transaction

@extend_schema(tags=['Transaction'], deprecated=True)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    transactions = Transaction.objects.filter(
        user=request.user,
    )

    serializer = TransactionSerializer(transactions, many=True)

    return Response({
        'transactions': serializer.data,
    }, status=200)