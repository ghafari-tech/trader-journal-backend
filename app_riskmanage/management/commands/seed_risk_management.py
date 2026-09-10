import random

from django.core.management.base import BaseCommand

from app_portfolio.models import Portfolio
from app_riskmanage.models import RiskManagement


class Command(BaseCommand):
    help = "Seed risk management for portfolios"

    def handle(self, *args, **options):
        portfolios = Portfolio.objects.all()

        created_count = 0
        skipped_count = 0

        for portfolio in portfolios:

            # اگر از قبل RiskManagement دارد، دست نزن
            if RiskManagement.objects.filter(
                portfolio=portfolio
            ).exists():
                skipped_count += 1
                continue

            RiskManagement.objects.create(
                portfolio=portfolio,
                max_risk=random.randint(1, 5),
                max_loss_daily=random.randint(2, 8),
                max_loss_weekly=random.randint(5, 15),
                max_transaction_daily=random.randint(3, 10),
                max_consecutive_loss=random.randint(2, 5),
                min_r_r=random.randint(1, 3),
            )

            created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created RiskManagement for: {portfolio.name}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} | "
                f"Skipped: {skipped_count}"
            )
        )
