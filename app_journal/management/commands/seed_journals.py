import random

from django.core.management.base import BaseCommand

from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from app_journal.models import Journal


class Command(BaseCommand):
    help = "Seed journals for portfolios"

    def handle(self, *args, **options):

        portfolios = Portfolio.objects.all()

        created_count = 0
        skipped_count = 0

        titles = [
            "بررسی معامله",
            "تحلیل عملکرد",
            "بررسی اشتباه",
            "ثبت تجربه معامله",
            "بررسی احساسات",
            "تحلیل ورود",
            "تحلیل خروج",
            "مرور پلن معاملاتی",
            "بررسی مدیریت ریسک",
            "درس امروز",
        ]

        feels = [
            "comfort",
            "concentrated",
            "greed",
            "fear",
            "revenge",
        ]

        mistakes = [
            "ورود کمی زودتر از برنامه انجام شد.",
            "حد ضرر مطابق برنامه تنظیم نشد.",
            "قبل از ورود تحلیل بیشتری لازم بود.",
            "حجم معامله کمی بیشتر از حد مناسب بود.",
            "معامله کاملاً مطابق پلن انجام شد.",
            "در زمان ورود احساسات کمی تأثیرگذار بود.",
            "باید صبر بیشتری برای تأیید می‌کردم.",
            "خروج معامله بهتر از چیزی که انتظار داشتم انجام شد.",
            "مدیریت ریسک مناسب بود.",
            "اشتباه مهمی در این معامله وجود نداشت.",
        ]

        lessons = [
            "باید بیشتر به پلن معاملاتی پایبند باشم.",
            "صبر برای تأیید ورود اهمیت زیادی دارد.",
            "مدیریت ریسک از نتیجه یک معامله مهم‌تر است.",
            "نباید تحت تأثیر احساسات تصمیم بگیرم.",
            "قبل از ورود باید سناریوی معامله مشخص باشد.",
            "حجم معامله باید با ریسک تعیین‌شده هماهنگ باشد.",
            "بعد از هر معامله باید نتیجه را بررسی کنم.",
            "نباید برای جبران ضرر وارد معامله شوم.",
            "رعایت پلن باعث تصمیم‌گیری بهتر می‌شود.",
            "این معامله تجربه خوبی برای معاملات بعدی بود.",
        ]

        for portfolio in portfolios:

            transactions = list(
                Transaction.objects.filter(
                    portfolio=portfolio
                )
            )

            if not transactions:
                skipped_count += 1
                continue

            # برای هر Portfolio بین 25 تا 60 ژورنال
            journal_count = random.randint(25, 60)

            for _ in range(journal_count):

                transaction = random.choice(transactions)

                Journal.objects.create(
                    transaction=transaction,
                    portfolio=portfolio,
                    title=random.choice(titles),
                    feel=random.choice(feels),
                    mistakes=random.choice(mistakes),
                    lesson_learned=random.choice(lessons),
                    followed_plan=random.choice(
                        [True, True, True, False]
                    ),
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {journal_count} journals "
                    f"for: {portfolio.name}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} journals | "
                f"Skipped portfolios: {skipped_count}"
            )
        )
