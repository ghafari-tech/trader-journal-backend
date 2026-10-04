from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from app_setting.models import Subscription


class DiscountCode(models.Model):
    code = models.CharField(max_length=50)
    percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('code'),
                name='unique_discount_code_ci',
            ),
        ]

    def __str__(self):
        return self.code

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.used_count >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True


class Payment(models.Model):
    authority = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    original_amount = models.PositiveIntegerField(default=0)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    discount_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )