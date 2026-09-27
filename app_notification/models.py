from app_user.models import User
from django.db import models

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    icon = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class NotificationSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_settings')
    add_journal_notif = models.BooleanField(default=False)
    risk_up_warning_notif = models.BooleanField(default=True)
    ai_report_weekly_mail = models.BooleanField(default=False)
    fomo_notif = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
