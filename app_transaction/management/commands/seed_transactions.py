import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from app_journal.models import Transaction
from app_user.models import User


class Command(BaseCommand):
    help = "Create fake transactions"

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=50,
        )

    def handle(self, *args, **options):
        count = options["count"]

        user = User.objects.first()

        if not user:
            self.stdout.write(
                self.style.ERROR("No user found.")
            )
            return

        symbols = [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "XAUUSD",
            "BTCUSD",
            "US30",
            "NAS100",
        ]

        transaction_types = [
            "buy",
            "sell",
        ]

        created = 0

        for _ in range(count):

            transaction_type = random.choice(transaction_types)
            symbol = random.choice(symbols)

            entry_price = Decimal(
                str(round(random.uniform(1, 3000), 5))
            )

            exit_price = Decimal(
                str(round(
                    float(entry_price) *
                    random.uniform(0.98, 1.02),
                    5
                ))
            )

            volume = Decimal(
                str(random.choice([
                    0.01,
                    0.02,
                    0.05,
                    0.10,
                    0.20,
                    0.50,
                    1.00,
                ]))
            )

            profit_loss = Decimal(
                str(round(
                    random.uniform(-500, 1000),
                    2
                ))
            )

            risk_reward = Decimal(
                str(round(
                    random.uniform(0.5, 5),
                    2
                ))
            )

            transaction = Transaction.objects.create(
                user=user,
                symbol=symbol,
                transaction_type=transaction_type,
                entry_price=entry_price,
                exit_price=exit_price,
                volume=volume,
                risk_reward=risk_reward,
                profit_loss=profit_loss,
                followed_plan=random.choice([True, False]),
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created} fake transactions created successfully."
            )
        )