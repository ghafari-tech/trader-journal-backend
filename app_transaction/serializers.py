from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


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