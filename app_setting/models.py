from django.db import models

class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class SubscriptionFeature(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='feature')
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value