from django.db import models
from app_portfolio.models import Portfolio
from app_user.models import User


class RiskManagement(models.Model):
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    max_risk = models.IntegerField(default=0)
    max_loss_daily = models.IntegerField(default=0)
    max_loss_weekly = models.IntegerField(default=0)
    max_transaction_daily = models.IntegerField(default=0)
    max_consecutive_loss = models.IntegerField(default=0)
    min_r_r = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
