from django.db import models
from django.conf import settings
from app_setting.models import Subscription

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    authority = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name} - {self.is_paid}"

