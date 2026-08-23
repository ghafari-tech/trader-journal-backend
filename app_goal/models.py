from app_user.models import User
from django.db import models

class Goal(models.Model):

    TYPE_CHOICES = [
        ("profit", "سود"),
        ("risk", "ریسک"),
        ("order", "نظم"),
        ("learning", "یادگیری")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    title = models.CharField(max_length=255)
    target_type = models.CharField(
        max_length=8,
        choices=TYPE_CHOICES
    )
    target_value = models.IntegerField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
