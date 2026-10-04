from rest_framework import serializers
from .models import Badge, UserBadge


class BadgeSerializer(serializers.ModelSerializer):
    is_finished = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    finished_at = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'icon',
            'trigger_type', 'trigger_count', 'order',
            'is_finished', 'progress', 'finished_at',
        ]

    def _ub(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        return obj.user_badges.filter(user=request.user).first()

    def get_is_finished(self, obj):
        ub = self._ub(obj)
        return ub.is_finished if ub else False

    def get_progress(self, obj):
        ub = self._ub(obj)
        return ub.progress if ub else 0

    def get_finished_at(self, obj):
        ub = self._ub(obj)
        return ub.finished_at if ub and ub.finished_at else None


class AddBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon', 'trigger_type', 'trigger_count', 'order']


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source='badge.name', read_only=True)
    badge_description = serializers.CharField(source='badge.description', read_only=True)
    badge_icon = serializers.CharField(source='badge.icon', read_only=True)

    class Meta:
        model = UserBadge
        fields = [
            'id', 'badge', 'badge_name', 'badge_description', 'badge_icon',
            'is_finished', 'progress', 'finished_at',
        ]