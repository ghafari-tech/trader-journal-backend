from rest_framework import serializers
from app_user.models import Subscription, User

class UserPlanSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'user',
            'type_display',
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