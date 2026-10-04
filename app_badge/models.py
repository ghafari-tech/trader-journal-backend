from django.db import models
from app_user.models import User


class Badge(models.Model):
    TRIGGER_CHOICES = [
        ('plan_streak', 'روزهای متوالی پایبند به پلن'),
        ('drawdown_reduction', 'کاهش دراودان'),
        ('no_revenge_trade', 'روزهای بدون Revenge Trade'),
        ('trade_count', 'تعداد معاملات'),
        ('profit_factor', 'Profit Factor'),
        ('no_emotional_entry', 'روزهای بدون ورود احساسی'),
        ('first_trade', 'اولین معامله'),
        ('journal_streak', 'روزهای متوالی ژورنال‌نویسی'),
        ('profitable_month', 'ماه سودده'),
        ('win_rate', 'Win Rate'),
        ('risk_management', 'مدیریت ریسک'),
        ('no_overtrading', 'بدون Overtrading'),
        ('capital_double', 'دابل کردن سرمایه'),
        ('a_plus_streak', 'معاملات A+ متوالی'),
        ('mt_connection', 'اتصال متاتریدر'),
        ('checklist_master', 'استاد چک‌لیست'),
    ]

    STREAK_TRIGGERS = {
        'journal_streak',
        'plan_streak',
        'no_revenge_trade',
        'no_emotional_entry',
        'no_overtrading',
    }

    name = models.CharField(max_length=100)
    description = models.TextField()
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    trigger_count = models.PositiveIntegerField(default=1)
    icon = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    acquisition_by = models.ManyToManyField(
        User,
        through='UserBadge',
        related_name='badges',
        blank=True,
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    is_finished = models.BooleanField(default=False)
    progress = models.PositiveIntegerField(default=0)
    last_progress_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f'{self.user_id} - {self.badge.name} ({self.progress}/{self.badge.trigger_count})'