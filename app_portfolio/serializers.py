from rest_framework import serializers
from .models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class AddPortfolioSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    broker = serializers.CharField()
    balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    currency = serializers.ChoiceField(
        choices=[
            'USD',
            'USDT',
            'EUR',
            'IRR'
        ]
    )
    leverage = serializers.ChoiceField(
        choices=[
            '1:1',
            '1:30',
            '1:100',
            '1:200',
            '1:500'
        ]
    )

    class Meta:
        model = Portfolio
        fields = [
            'name',
            'broker',
            'balance',
            'currency',
            'leverage',
        ]