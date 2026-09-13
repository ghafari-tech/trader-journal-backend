import random

from django.core.management.base import BaseCommand

from app_user.models import User
from app_portfolio.models import Portfolio


class Command(BaseCommand):
    help = "Seed portfolios for users who don't have any portfolio"

    def handle(self, *args, **options):
        users = User.objects.all()

        created_count = 0
        skipped_count = 0

        brokers = [
            "IC Markets",
            "XM",
            "Exness",
            "FTMO",
            "Pepperstone",
            "RoboForex",
        ]

        portfolio_names = [
            "Main Account",
            "Trading Account",
            "Forex Account",
            "Personal Account",
            "Scalping Account",
            "Swing Account",
            "Investment Account",
            "Prop Account",
            "Demo Account",
            "Strategy Account",
        ]

        currencies = ["USD", "EUR", "USDT"]

        leverages = [
            "1:30",
            "1:100",
            "1:200",
            "1:500",
        ]

        for user in users:

            # اگر کاربر حتی یک Portfolio داشته باشد،
            # هیچ Portfolio جدیدی برای او ساخته نمی‌شود.
            if user.portfolios.exists():
                skipped_count += 1
                continue

            portfolio_count = random.randint(7, 10)

            for i in range(portfolio_count):
                Portfolio.objects.create(
                    user=user,
                    name=f"{random.choice(portfolio_names)} {i + 1}",
                    broker=random.choice(brokers),
                    balance=random.randint(1000, 100000),
                    profit_loss=0,
                    transactions_count=0,
                    leverage=random.choice(leverages),
                    currency=random.choice(currencies),
                    profit_percentage=0,
                    is_active=(i == 0),
                    is_archived=False,
                    mt_connection=False,
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {portfolio_count} portfolios for user: {user.email}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} portfolios | "
                f"Skipped users: {skipped_count}"
            )
        )
