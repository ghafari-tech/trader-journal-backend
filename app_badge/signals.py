from django.db.models.signals import post_save
from django.dispatch import receiver

from app_transaction.models import Transaction, MetaTraderAccount
from app_journal.models import Journal
from .services import unlock, unlock_streak


@receiver(post_save, sender=Transaction)
def on_transaction_saved(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.portfolio.user
    unlock(user, 'first_trade')
    unlock(user, 'trade_count')


@receiver(post_save, sender=MetaTraderAccount)
def on_mt_account_saved(sender, instance, created, **kwargs):
    if not created:
        return
    unlock(instance.portfolio.user, 'mt_connection')


@receiver(post_save, sender=Journal)
def on_journal_saved(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.portfolio.user

    unlock_streak(user, 'journal_streak')

    if instance.followed_plan:
        unlock_streak(user, 'plan_streak')

    if instance.feel != 'revenge':
        unlock_streak(user, 'no_revenge_trade')

    if instance.feel not in ('greed', 'fear', 'revenge'):
        unlock_streak(user, 'no_emotional_entry')