from django.db import models
from django.core.validators import RegexValidator
from app_user.models import User


class Transaction(models.Model):

    TYPE_CHOICES = [
        ("buy", "خرید"),
        ("sell", "فروش"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")

    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        validators=[
            RegexValidator(
                regex=r"^T-\d+$",
                message="Transaction ID must be in the format T-123."
            )
        ],
    )

    symbol = models.CharField(
        max_length=20
    )

    transaction_type = models.CharField(
        max_length=4,
        choices=TYPE_CHOICES
    )

    entry_price = models.DecimalField(
        max_digits=20,
        decimal_places=8
    )

    exit_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )

    volume = models.DecimalField(
        max_digits=20,
        decimal_places=8
    )

    risk_reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    profit_loss = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    followed_plan = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            last_transaction = Transaction.objects.order_by("-id").first()

            if last_transaction:
                last_number = int(
                    last_transaction.transaction_id.split("-")[1]
                )
                number = last_number + 1
            else:
                number = 1

            self.transaction_id = f"T-{number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.transaction_id