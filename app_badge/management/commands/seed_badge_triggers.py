from django.core.management.base import BaseCommand
from app_badge.models import Badge


MAPPING = {
    1:  ('plan_streak', 7),
    2:  ('drawdown_reduction', 1),
    3:  ('no_revenge_trade', 30),
    4:  ('trade_count', 100),
    5:  ('profit_factor', 1),
    6:  ('no_emotional_entry', 30),
    7:  ('first_trade', 1),
    8:  ('journal_streak', 30),
    9:  ('profitable_month', 1),
    10: ('win_rate', 1),
    11: ('risk_management', 50),
    12: ('no_overtrading', 14),
    13: ('capital_double', 1),
    14: ('a_plus_streak', 10),
    15: ('mt_connection', 1),
    16: ('checklist_master', 50),
}


class Command(BaseCommand):
    help = 'Set trigger_type and trigger_count for existing badges'

    def handle(self, *args, **kwargs):
        for order, (badge_id, (trigger, count)) in enumerate(MAPPING.items(), start=1):
            updated = Badge.objects.filter(id=badge_id).update(
                trigger_type=trigger,
                trigger_count=count,
                order=order,
            )
            self.stdout.write(f'badge {badge_id}: updated={updated}')
        self.stdout.write(self.style.SUCCESS('done'))