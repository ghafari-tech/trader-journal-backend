from rest_framework import serializers
from app_user.models import Subscription

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