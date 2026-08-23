from django.db import models
from app_transaction.models import Transaction
from app_user.models import User


class Journal(models.Model):
    FEEL_CHOICES = [
        ("comfort", "آرام"),
        ("concentrated", "متمرکز"),
        ("greed", "طمع"),
        ("fear", "ترس"),
        ("revenge", "انتقام")
    ]
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, related_name='journals', null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='journals', null=True)
    title = models.CharField(max_length=100)
    feel = models.CharField(
        max_length=20,
        choices=FEEL_CHOICES,
        default='comfort',
    )
    mistakes = models.TextField()
    lesson_learned = models.TextField()
    followed_plan = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

