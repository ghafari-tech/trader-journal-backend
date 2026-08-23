from rest_framework import serializers
from .models import Journal

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = '__all__'

class AddJournalSerializer(serializers.Serializer):
    title = serializers.CharField()
    transaction_id = serializers.CharField()
    feel = serializers.ChoiceField(
        choices=[
            "comfort",
            "concentrated",
            "greed",
            "fear",
            "revenge",
        ]
    )
    mistakes = serializers.CharField()
    lesson_learned = serializers.CharField()
    followed_plan = serializers.BooleanField()