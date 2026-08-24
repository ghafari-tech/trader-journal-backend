from django.db import models
from app_user.models import User


class Portfolio(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolios'
    )

    name = models.CharField(max_length=100)
    broker = models.CharField(max_length=100)

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    profit_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    transactions_count = models.PositiveIntegerField(default=0)

    leverage = models.PositiveIntegerField(default=1)

    currency = models.CharField(max_length=10, default='USD')

    profit_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    mt_connection = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name