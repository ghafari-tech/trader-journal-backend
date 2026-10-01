from django.db import models

from app_portfolio.models import Portfolio

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    description = models.TextField()
    api_key = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    

class AIAnalysis(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='ai_analyses')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    weekly_report = models.TextField()
    trading_regime = models.IntegerField(default=0) # Scoring from 0 to 100
    capital_management = models.IntegerField(default=0) # Scoring from 0 to 100
    psychology = models.IntegerField(default=0) # Scoring from 0 to 100
    adherence_to_the_plan = models.IntegerField(default=0) # Scoring from 0 to 100
    date = models.DateTimeField(auto_now_add=True)


class Strengths(models.Model):
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    maintaining_sustainability = models.TextField()

class Weaknesses(models.Model):
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    solution = models.TextField()

class PerformanceReportDay(models.Model):
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    transaction_count = models.IntegerField(default=0)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2) # Profit amount in dollars (negative and positive)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    adherence_to_the_plan = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    best_trade = models.TextField() # A brief explanation of artificial intelligence
    worst_trade = models.TextField() # A brief explanation of artificial intelligence
    golden_window = models.TextField() # A brief explanation of artificial intelligence

class PerformanceReportWeek(models.Model):
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE)
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    description = models.TextField()
    transaction_count = models.IntegerField(default=0)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2) # Profit amount in dollars (negative and positive)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    adherence_to_the_plan = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    best_trade = models.TextField() # A brief explanation of artificial intelligence
    worst_trade = models.TextField() # A brief explanation of artificial intelligence
    golden_window = models.TextField() # A brief explanation of artificial intelligence

class SuggestedExercises(models.Model):
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE)
    text = models.TextField() # A brief explanation of artificial intelligence