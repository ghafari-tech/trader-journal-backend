from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class AddTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'symbol',
            'transaction_type',
            'entry_price',
            'exit_price',
            'volume',
            'stop_loss',
            'take_profit',
            'risk_reward',
            'profit_loss',
            'followed_plan',
            'r_r',
            'closed_at',
        ]
        extra_kwargs = {
            'exit_price': {'required': False, 'allow_null': True},
            'stop_loss': {'required': False, 'allow_null': True},
            'take_profit': {'required': False, 'allow_null': True},
            'risk_reward': {'required': False, 'allow_null': True},
            'profit_loss': {'required': False, 'allow_null': True},
            'r_r': {'required': False, 'allow_null': True},
            'closed_at': {'required': False, 'allow_null': True},
            'followed_plan': {'required': False},
        }


class ImportMetaTraderReportSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    file = serializers.FileField(
        help_text="MetaTrader HTML report file."
    )

    def validate_file(self, value):
        if not value.name.lower().endswith((".html", ".htm")):
            raise serializers.ValidationError(
                "Only HTML files are allowed."
            )

        return value