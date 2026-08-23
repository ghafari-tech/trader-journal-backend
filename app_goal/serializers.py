from rest_framework import serializers
from .models import Goal

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

class GoalInformationSerializer(serializers.Serializer):
    title = serializers.CharField()
    target_type = serializers.ChoiceField(
        choices=[
            "profit",
            "risk",
            "order",
            "learning"
        ]
    )
    target_value = serializers.IntegerField()
    deadline = serializers.DateTimeField()
