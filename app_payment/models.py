from django.conf import settings
from django.db import models

from app_setting.models import Subscription


class Payment(models.Model):
	authority = models.CharField(max_length=100, unique=True)
	amount = models.PositiveIntegerField()
	ref_id = models.CharField(max_length=100, blank=True, null=True)
	is_paid = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='payments',
	)
