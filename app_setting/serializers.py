from rest_framework import serializers

from app_notification.models import NotificationSettings
from app_user.models import UserSubscription, User

class UserPlanSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user',
            'type',
            'type_name',
            'start_date',
            'end_date',
        ]

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'image_profile'
        ]

class MetaTraderConnectSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=['mt4', 'mt5'])
    server = serializers.CharField(max_length=100)
    account_number = serializers.CharField(max_length=50)


class UpdateNotificationSettingsSerializer(serializers.Serializer):
    field = serializers.ChoiceField(
        choices=[
            "add_journal_notif",
            "risk_up_warning_notif",
            "ai_report_weekly_mail",
            "fomo_notif",
        ]
    )
    value = serializers.BooleanField()