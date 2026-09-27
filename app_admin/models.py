from django.db import models

class Api_Ai(models.Model):
    name = models.CharField(max_length=100)
    API = models.CharField(max_length=100)
    requests_token = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name