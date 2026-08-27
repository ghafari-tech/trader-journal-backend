from rest_framework import serializers
from app_transaction.models import Transaction


class TransactionDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['symbol', 'transaction_type', 'volume', 'r_r', 'total_reward', 'created_at']


class BestTransactionDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['symbol', 'total_reward', 'r_r', 'created_at']