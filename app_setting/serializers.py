from rest_framework import serializers

from app_notification.models import NotificationSettings
from app_setting.models import Subscription
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


class UpdateUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'image_profile'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'phone': {'required': False, 'allow_null': True},
            'image_profile': {'required': False},
        }

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    def validate_phone(self, value):
        if value in (None, ''):
            return None
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(phone=value).exists():
            raise serializers.ValidationError('This phone is already in use.')
        return value

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


class PlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"