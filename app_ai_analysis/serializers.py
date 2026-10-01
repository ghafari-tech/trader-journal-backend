from rest_framework import serializers
from .models import *

class StrengthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strengths
        fields = '__all__'

class WeaknessesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weaknesses
        fields = '__all__'

class PerformanceReportDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReportDay
        fields = '__all__'

class PerformanceReportWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReportWeek
        fields = '__all__'

class SuggestedExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedExercises
        fields = '__all__'

class AIAnalysisSerializer(serializers.ModelSerializer):
    strengths = StrengthsSerializer(source='strengths_set', many=True, read_only=True)
    weaknesses = WeaknessesSerializer(source='weaknesses_set', many=True, read_only=True)
    performance_days = PerformanceReportDaySerializer(source='performancereportday_set', many=True, read_only=True)
    performance_weeks = PerformanceReportWeekSerializer(source='performancereportweek_set', many=True, read_only=True)
    suggested_exercises = SuggestedExercisesSerializer(source='suggestedexercises_set', many=True, read_only=True)

    class Meta:
        model = AIAnalysis
        fields = '__all__'

class RegenerateAIAnalysisRequestSerializer(serializers.ModelSerializer):
    models_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = AIAnalysisRequest
        fields = ['models_id']