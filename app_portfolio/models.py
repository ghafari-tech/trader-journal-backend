from django.db import models
from app_user.models import User


class Portfolio(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('USDT', 'USDT'),
        ('IRR', 'IRR')
    ]

    LEVERAGE_CHOICES = [
        ('1:1', '1:1'),
        ('1:30', '1:30'),
        ('1:100', '1:100'),
        ('1:200', '1:200'),
        ('1:500', '1:500'),
    ]

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
    leverage = models.CharField(default='1:1', choices=LEVERAGE_CHOICES, max_length=10)
    currency = models.CharField(max_length=10, default='USD', choices=CURRENCY_CHOICES)
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