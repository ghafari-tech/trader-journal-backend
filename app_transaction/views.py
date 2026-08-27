from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import Transaction

@extend_schema(tags=['Transaction'])
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

def transaction_list_dashboard(request):
    transactions = Transaction.objects.filter(
        user=request.user,
    )

    serializer = TransactionDashboardSerializer(transactions, many=True)

    return Response({
        'transactions': serializer.data,
    }, status=200)


def dashboard(request):
    transactions = Transaction.objects.filter(
        user=request.user,
    )
    transaction_serializer = TransactionDashboardSerializer(transactions, many=True)

    best_transaction = Transaction.objects.filter(
        user=request.user,
    ).order_by('total_reward').first()
    best_transaction_serializer = BestTransactionDashboardSerializer(best_transaction)

    badest_transaction = Transaction.objects.filter(
        user=request.user,
    ).order_by('-total_reward').first()
    badest_transaction_serilizer = BestTransactionDashboardSerializer(badest_transaction)

    total_reward = transactions.aggregate(Sum('total_reward'))

    total_reward_percent = total_reward.get('total_reward__percent')


    return Response({
        'transactions': transaction_serializer.data,
        'best_transaction': best_transaction_serializer.data,
        'badest_transaction': badest_transaction_serilizer.data,
    })