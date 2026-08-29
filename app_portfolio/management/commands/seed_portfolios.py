from decimal import Decimal
from random import choice, randint, uniform

from django.core.management.base import BaseCommand

from app_portfolio.models import Portfolio
from app_user.models import User


class Command(BaseCommand):
    help = "Create fake portfolios for all users"

    def handle(self, *args, **options):

        users = User.objects.all()

        if not users.exists():
            self.stdout.write(
                self.style.ERROR("No users found.")
            )
            return

        brokers = [
            "MetaTrader",
            "IC Markets",
            "XM",
            "Exness",
            "Pepperstone",
            "FTMO",
        ]

        portfolio_names = [
            "Main Account",
            "Forex Account",
            "Crypto Account",
            "Trading Account",
            "Investment",
            "Scalping",
            "Swing Trading",
        ]

        currencies = [
            "USD",
            "EUR",
            "USDT",
        ]

        leverages = [
            "1:30",
            "1:100",
            "1:200",
            "1:500",
        ]

        created_count = 0

        for user in users:

            # برای هر کاربر 2 تا 4 پورتفولیو
            portfolio_count = randint(2, 4)

            for i in range(portfolio_count):

                currency = choice(currencies)

                # موجودی اولیه
                balance = Decimal(
                    str(
                        round(
                            uniform(1000, 50000),
                            2
                        )
                    )
                )

                portfolio = Portfolio.objects.create(
                    user=user,

                    name=f"{choice(portfolio_names)} {i + 1}",

                    broker=choice(brokers),

                    balance=balance,

                    profit_loss=Decimal("0"),

                    transactions_count=0,

                    leverage=choice(leverages),

                    currency=currency,

                    profit_percentage=Decimal("0"),

                    is_active=True,

                    is_archived=False,

                    mt_connection=choice([
                        True,
                        False,
                    ]),
                )

                created_count += 1

                self.stdout.write(
                    f"Created portfolio '{portfolio.name}' "
                    f"for user {user.id}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{created_count} fake portfolios created successfully."
            )
        )