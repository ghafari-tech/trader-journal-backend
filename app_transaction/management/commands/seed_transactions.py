from decimal import Decimal
from random import choice, randint, uniform

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_portfolio.models import Portfolio
from app_transaction.models import Transaction


class Command(BaseCommand):
    help = "Create fake transactions for all portfolios"

    def handle(self, *args, **options):

        portfolios = Portfolio.objects.all()

        if not portfolios.exists():
            self.stdout.write(
                self.style.ERROR("No portfolios found.")
            )
            return

        symbols = [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "XAUUSD",
            "BTCUSD",
            "ETHUSD",
        ]

        created_count = 0

        for portfolio in portfolios:

            # برای هر Portfolio بین 10 تا 20 معامله
            transaction_count = randint(10, 20)

            for _ in range(transaction_count):

                transaction_type = choice([
                    "buy",
                    "sell",
                ])

                symbol = choice(symbols)

                entry_price = Decimal(
                    str(round(uniform(1, 50000), 4))
                )

                # حدود 40٪ معاملات سودده
                is_profit = choice([
                    True,
                    True,
                    True,
                    False,
                    False,
                ])

                if is_profit:

                    change = Decimal(
                        str(round(uniform(0.01, 0.08), 4))
                    )

                else:

                    change = Decimal(
                        str(round(uniform(0.01, 0.05), 4))
                    )

                if transaction_type == "buy":

                    if is_profit:
                        exit_price = entry_price * (
                            Decimal("1") + change
                        )
                    else:
                        exit_price = entry_price * (
                            Decimal("1") - change
                        )

                else:

                    if is_profit:
                        exit_price = entry_price * (
                            Decimal("1") - change
                        )
                    else:
                        exit_price = entry_price * (
                            Decimal("1") + change
                        )

                volume = Decimal(
                    str(round(uniform(0.01, 2), 4))
                )

                transaction = Transaction(
                    portfolio=portfolio,
                    symbol=symbol,
                    transaction_type=transaction_type,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    volume=volume,
                    risk_reward=Decimal(
                        str(round(uniform(1, 4), 2))
                    ),
                    followed_plan=choice([
                        True,
                        False,
                    ]),
                    r_r=Decimal(
                        str(round(uniform(1, 4), 2))
                    ),
                    closed_at=timezone.now()
                    - timezone.timedelta(
                        days=randint(0, 29),
                        hours=randint(0, 23),
                        minutes=randint(0, 59),
                    ),
                )

                # profit_loss داخل save() مدل محاسبه می‌شود
                transaction.save()

                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} fake transactions created successfully."
            )
        )