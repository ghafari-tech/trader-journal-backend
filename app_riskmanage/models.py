from django.db import models
from app_portfolio.models import Portfolio
from app_user.models import User


class RiskManagement(models.Model):
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    max_risk = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_loss_daily = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_loss_weekly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_transaction_daily = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_consecutive_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_r_r = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id)
