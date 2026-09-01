from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class MT5VerifyInternalSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=50)
    investor_password = serializers.CharField(max_length=255)
    server = serializers.CharField(max_length=100)