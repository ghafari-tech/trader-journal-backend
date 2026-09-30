from rest_framework import serializers
from app_user.models import UserSubscription


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

class UserPlanSerializer(serializers.Serializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'