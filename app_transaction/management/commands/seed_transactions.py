import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from app_portfolio.models import Portfolio
from app_transaction.models import Transaction


SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "NZDUSD", "XAUUSD", "US30", "BTCUSD", "ETHUSD",
]


class Command(BaseCommand):
    help = "برای پورتفوی‌هایی که کمتر از ۵ معامله دارند، بین ۵۰ تا ۱۰۰ معامله تصادفی می‌سازد."

    def add_arguments(self, parser):
        parser.add_argument("--min", type=int, default=50)
        parser.add_argument("--max", type=int, default=100)
        parser.add_argument("--threshold", type=int, default=5)

    def handle(self, *args, **options):
        min_trades = options["min"]
        max_trades = options["max"]
        threshold = options["threshold"]

        portfolios = Portfolio.objects.all()
        total_created = 0

        for portfolio in portfolios:
            existing = Transaction.objects.filter(portfolio=portfolio).count()
            if existing >= threshold:
                self.stdout.write(
                    f"پورتفوی {portfolio.id} رد شد (دارای {existing} معامله)"
                )
                continue

            count = random.randint(min_trades, max_trades)
            created = self._create_for_portfolio(portfolio, count)
            total_created += created
            self.stdout.write(
                self.style.SUCCESS(
                    f"پورتفوی {portfolio.id}: {created} معامله ساخته شد"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"مجموع معاملات ساخته‌شده: {total_created}"))

    @transaction.atomic
    def _create_for_portfolio(self, portfolio, count):
        now = timezone.now()
        created_count = 0

        for _ in range(count):
            symbol = random.choice(SYMBOLS)
            trade_type = random.choice(["buy", "sell"])

            entry_price = Decimal(str(round(random.uniform(0.5, 2500), 4)))
            volume = Decimal(str(round(random.uniform(0.01, 5.0), 2)))

            stop_loss = (entry_price * Decimal("0.99")).quantize(Decimal("0.00000001"))
            take_profit = (entry_price * Decimal("1.02")).quantize(Decimal("0.00000001"))

            is_win = random.random() < 0.55
            move = Decimal(str(round(random.uniform(0.002, 0.03), 6)))

            if trade_type == "buy":
                exit_price = (
                    entry_price * (Decimal("1") + move)
                    if is_win
                    else entry_price * (Decimal("1") - move)
                )
            else:
                exit_price = (
                    entry_price * (Decimal("1") - move)
                    if is_win
                    else entry_price * (Decimal("1") + move)
                )
            exit_price = exit_price.quantize(Decimal("0.00000001"))

            risk_reward = Decimal(str(round(random.uniform(1.0, 3.5), 2)))
            r_r = Decimal(str(round(random.uniform(-3.0, 4.0), 2)))
            followed_plan = random.random() < 0.7

            days_ago = random.randint(1, 90)
            created_at = now - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            closed_at = created_at + timedelta(hours=random.randint(1, 48))

            tx = Transaction.objects.create(
                portfolio=portfolio,
                symbol=symbol,
                transaction_type=trade_type,
                entry_price=entry_price,
                exit_price=exit_price,
                volume=volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward=risk_reward,
                followed_plan=followed_plan,
                r_r=r_r,
                closed_at=closed_at,
            )

            # چون created_at از نوع auto_now_add است، باید دستی override شود
            Transaction.objects.filter(pk=tx.pk).update(created_at=created_at)
            created_count += 1

        return created_count