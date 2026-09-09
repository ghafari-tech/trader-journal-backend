from django.db import models
from app_user.models import User


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    acquisition_by = models.ManyToManyField(User, related_name='badges')

    def __str__(self):
        return self.name