import random
from django.core.management.base import BaseCommand

from app_user.models import User, Subscription


class Command(BaseCommand):
    help = "Seed subscriptions for users"

    def handle(self, *args, **options):
        users = User.objects.all()

        created_count = 0
        skipped_count = 0

        for user in users:
            if Subscription.objects.filter(user=user).exists():
                skipped_count += 1
                continue

            subscription_type = random.choice([
                "",
                "pro",
                "pro max",
            ])

            Subscription.objects.create(
                user=user,
                type=subscription_type,
            )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count} | Skipped: {skipped_count}"
            )
        )
