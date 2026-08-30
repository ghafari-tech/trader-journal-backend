from rest_framework import serializers
from app_user.models import User


class UserAdminSerializer(serializers.ModelSerializer):
    subscription_type = serializers.CharField(
        source="plan.type",
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "subscription_type",
            "status",
            "created_at",
        ]