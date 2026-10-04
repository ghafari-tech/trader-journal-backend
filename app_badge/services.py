from datetime import timedelta
from django.utils import timezone
from .models import Badge, UserBadge
from app_notification.models import Notification


def _notify(user, badge):
    Notification.objects.create(
        user=user,
        title='🏆 نشان جدید دریافت کردید',
        body=f'شما نشان «{badge.name}» را دریافت کردید.',
        icon=badge.icon or 'badge',
        is_active=True,
    )


def _finish(ub, badge, user, unlocked):
    ub.is_finished = True
    ub.finished_at = timezone.now()
    unlocked.append(badge)
    _notify(user, badge)


def unlock(user, trigger_type, value=1):
    unlocked = []
    for badge in Badge.objects.filter(trigger_type=trigger_type):
        ub, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
        if ub.is_finished:
            continue
        ub.progress += value
        ub.last_progress_at = timezone.now()
        if ub.progress >= badge.trigger_count:
            _finish(ub, badge, user, unlocked)
        ub.save()
    return unlocked


def unlock_streak(user, trigger_type):
    today = timezone.now().date()
    unlocked = []
    for badge in Badge.objects.filter(trigger_type=trigger_type):
        ub, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
        if ub.is_finished:
            continue

        if ub.last_progress_at is None:
            ub.progress = 1
        else:
            last_date = ub.last_progress_at.date()
            if last_date == today:
                continue
            elif last_date == today - timedelta(days=1):
                ub.progress += 1
            else:
                ub.progress = 1

        ub.last_progress_at = timezone.now()
        if ub.progress >= badge.trigger_count:
            _finish(ub, badge, user, unlocked)
        ub.save()
    return unlocked


def reset_streak(user, trigger_type):
    for badge in Badge.objects.filter(trigger_type=trigger_type):
        UserBadge.objects.filter(
            user=user, badge=badge, is_finished=False
        ).update(progress=0, last_progress_at=None)