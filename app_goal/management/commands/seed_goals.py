import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_goal.models import Goal
from app_portfolio.models import Portfolio


class Command(BaseCommand):
    help = "Seed goals for portfolios"

    def handle(self, *args, **options):

        portfolios = Portfolio.objects.all()

        created_count = 0
        skipped_count = 0

        goal_data = {
            "profit": [
                "رسیدن به سود ماهانه",
                "افزایش سودآوری معاملات",
                "رسیدن به تارگت سود",
                "ثبت ماه مثبت",
                "افزایش بازدهی پورتفولیو",
            ],
            "risk": [
                "کنترل ریسک معاملات",
                "کاهش ضررهای متوالی",
                "رعایت حداکثر ریسک",
                "کنترل ضرر روزانه",
                "بهبود مدیریت سرمایه",
            ],
            "order": [
                "پایبندی کامل به پلن",
                "رعایت قوانین ورود",
                "رعایت قوانین خروج",
                "ثبت ژورنال معاملات",
                "جلوگیری از معاملات احساسی",
            ],
            "learning": [
                "یادگیری تحلیل تکنیکال",
                "بررسی معاملات گذشته",
                "یادگیری مدیریت ریسک",
                "بهبود استراتژی معاملاتی",
                "مطالعه بازار",
            ],
        }

        target_ranges = {
            "profit": (500, 10000),
            "risk": (1, 10),
            "order": (10, 100),
            "learning": (5, 50),
        }

        for portfolio in portfolios:

            if Goal.objects.filter(
                portfolio=portfolio
            ).exists():
                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped: {portfolio.name} "
                        f"(already has goals)"
                    )
                )

                continue

            goal_count = random.randint(4, 8)

            for _ in range(goal_count):

                target_type = random.choice(
                    list(goal_data.keys())
                )

                title = random.choice(
                    goal_data[target_type]
                )

                min_value, max_value = target_ranges[
                    target_type
                ]

                target_value = random.randint(
                    min_value,
                    max_value
                )

                deadline = (
                    timezone.now()
                    + timedelta(
                        days=random.randint(7, 120)
                    )
                )

                Goal.objects.create(
                    portfolio=portfolio,
                    title=title,
                    target_type=target_type,
                    target_value=target_value,
                    deadline=deadline,
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {goal_count} goals "
                    f"for: {portfolio.name}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} goals | "
                f"Skipped portfolios: {skipped_count}"
            )
        )
