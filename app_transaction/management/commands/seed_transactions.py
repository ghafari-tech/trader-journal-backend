import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_portfolio.models import Portfolio
from app_transaction.models import Transaction


class Command(BaseCommand):
    help = "Seed transactions for portfolios"

    def handle(self, *args, **options):

        portfolios = Portfolio.objects.all()

        created_count = 0
        skipped_count = 0

        symbols = [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "AUDUSD",
            "USDCAD",
            "USDCHF",
            "NZDUSD",
            "XAUUSD",
            "BTCUSD",
            "ETHUSD",
        ]

        for portfolio in portfolios:

            # اگر این Portfolio قبلاً معامله دارد، دست نزن
            if Transaction.objects.filter(
                portfolio=portfolio
            ).exists():
                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped: {portfolio.name} "
                        f"(already has transactions)"
                    )
                )

                continue

            # حداقل 90 معامله
            transaction_count = random.randint(90, 140)

            current_time = timezone.now()

            for i in range(transaction_count):

                transaction_type = random.choice(
                    ["buy", "sell"]
                )

                symbol = random.choice(symbols)

                # قیمت‌های پایه برای نمادهای مختلف
                if symbol == "XAUUSD":
                    entry_price = Decimal(
                        random.uniform(1800, 2500)
                    ).quantize(Decimal("0.00001"))

                elif symbol in ["BTCUSD", "ETHUSD"]:
                    if symbol == "BTCUSD":
                        entry_price = Decimal(
                            random.uniform(30000, 120000)
                        ).quantize(Decimal("0.00001"))
                    else:
                        entry_price = Decimal(
                            random.uniform(1500, 5000)
                        ).quantize(Decimal("0.00001"))

                elif symbol == "USDJPY":
                    entry_price = Decimal(
                        random.uniform(100, 160)
                    ).quantize(Decimal("0.00001"))

                else:
                    entry_price = Decimal(
                        random.uniform(0.6, 2.0)
                    ).quantize(Decimal("0.00001"))

                # حدود تغییر قیمت
                price_change = Decimal(
                    random.uniform(0.001, 0.05)
                )

                # تقریباً نصف معاملات سودده و نصف زیان‌ده
                is_profitable = random.choice(
                    [True, True, True, False, False]
                )

                if is_profitable:
                    direction = 1
                else:
                    direction = -1

                if transaction_type == "buy":
                    exit_price = (
                        entry_price
                        + (
                            price_change
                            * direction
                        )
                    )
                else:
                    exit_price = (
                        entry_price
                        - (
                            price_change
                            * direction
                        )
                    )

                exit_price = exit_price.quantize(
                    Decimal("0.00001")
                )

                volume = Decimal(
                    random.uniform(0.01, 2.0)
                ).quantize(Decimal("0.01"))

                risk_reward = Decimal(
                    random.uniform(0.5, 4.0)
                ).quantize(Decimal("0.01"))

                r_r = Decimal(
                    random.uniform(0.5, 4.0)
                ).quantize(Decimal("0.01"))

                # تاریخ معاملات در 180 روز گذشته
                created_at = (
                    current_time
                    - timedelta(
                        days=random.randint(0, 180),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )
                )

                transaction = Transaction(
                    portfolio=portfolio,
                    symbol=symbol,
                    transaction_type=transaction_type,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    volume=volume,
                    risk_reward=risk_reward,
                    followed_plan=random.choice(
                        [True, True, True, False]
                    ),
                    r_r=r_r,
                    closed_at=created_at + timedelta(
                        minutes=random.randint(5, 1440)
                    ),
                )

                transaction.save()

                # چون created_at خودکار است، بعداً تاریخ تستی را تنظیم می‌کنیم
                Transaction.objects.filter(
                    pk=transaction.pk
                ).update(
                    created_at=created_at
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {transaction_count} transactions "
                    f"for: {portfolio.name}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} transactions | "
                f"Skipped portfolios: {skipped_count}"
            )
        )
