from rest_framework import serializers

from app_setting.models import Subscription


class PaymentRequestSerializer(serializers.Serializer):
    subscription_id = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all(),
    )


class PaymentRequestResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    authority = serializers.CharField()
    payment_url = serializers.URLField()


class PaymentVerifyResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    code = serializers.CharField()
    message = serializers.CharField()
    ref_id = serializers.CharField(required=False, allow_null=True)