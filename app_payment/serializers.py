from rest_framework import serializers
from .models import Payment

class PaymentRequestSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()

class PaymentVerifySerializer(serializers.Serializer):
    Authority = serializers.CharField()
    Status = serializers.CharField()
