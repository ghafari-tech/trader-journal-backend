from rest_framework import serializers
from .models import RiskManagement


class RiskManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskManagement
        fields = '__all__'

class EditRiskManageSerializer(serializers.Serializer):
    max_risk = serializers.CharField()
    max_loss_daily = serializers.CharField()
    max_loss_weekly = serializers.CharField()
    max_transaction_daily = serializers.CharField()
    max_consecutive_loss = serializers.CharField()
    min_r_r = serializers.CharField()