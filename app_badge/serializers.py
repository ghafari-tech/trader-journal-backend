from rest_framework import serializers
from .models import Badge


class BadgeSerializer(serializers.ModelSerializer):
    is_acquisition = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ['name', 'description', 'is_acquisition']

    def get_is_acquisition(self, obj):
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            return obj.acquisition_by.filter(id=request.user.id).exists()

        return False

class AddBadgeSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Badge
        fields = ['name', 'description']
