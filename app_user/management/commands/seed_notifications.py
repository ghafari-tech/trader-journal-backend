import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_user.models import User
from app_notification.models import Notification


class Command(BaseCommand):
    help = "Seed notifications for users"

    def handle(self, *args, **options):

        users = User.objects.all()

        created_count = 0
        skipped_count = 0

        notifications = [
            (
                "معامله جدید",
                "یک معامله جدید در پورتفولیو شما ثبت شد.",
                "trending-up",
            ),
            (
                "معامله بسته شد",
                "یکی از معاملات شما با موفقیت بسته شد.",
                "check-circle",
            ),
            (
                "یادآوری ژورنال",
                "فراموش نکنید معاملات اخیر خود را بررسی کنید.",
                "book-open",
            ),
            (
                "هدف جدید",
                "یک هدف جدید برای پورتفولیو شما ثبت شده است.",
                "target",
            ),
            (
                "هدف نزدیک است",
                "به زمان پایان یکی از اهداف شما نزدیک می‌شوید.",
                "clock",
            ),
            (
                "مدیریت ریسک",
                "وضعیت مدیریت ریسک پورتفولیو خود را بررسی کنید.",
                "shield",
            ),
            (
                "عملکرد ماهانه",
                "گزارش عملکرد ماهانه شما آماده بررسی است.",
                "bar-chart",
            ),
            (
                "روز معاملاتی",
                "عملکرد معاملات امروز خود را بررسی کنید.",
                "calendar",
            ),
            (
                "نکته معاملاتی",
                "قبل از ورود به معامله، پلن معاملاتی خود را بررسی کنید.",
                "lightbulb",
            ),
            (
                "یادآوری",
                "امروز عملکرد و تصمیم‌های معاملاتی خود را مرور کنید.",
                "bell",
            ),
        ]

        for user in users:

            # اگر کاربر قبلاً Notification دارد، دست نزن
            if Notification.objects.filter(
                user=user
            ).exists():
                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped: {user.email} "
                        f"(already has notifications)"
                    )
                )

                continue

            # تعداد زیاد Notification برای هر کاربر
            notification_count = random.randint(30, 60)

            now = timezone.now()

            for _ in range(notification_count):

                title, body, icon = random.choice(
                    notifications
                )

                created_at = (
                    now
                    - timedelta(
                        days=random.randint(0, 180),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )
                )

                notification = Notification.objects.create(
                    user=user,
                    title=title,
                    body=body,
                    icon=icon,
                    is_read=random.choice(
                        [True, True, False]
                    ),
                    is_active=True,
                )

                # ساخت تاریخ تستی در گذشته
                Notification.objects.filter(
                    pk=notification.pk
                ).update(
                    created_at=created_at
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {notification_count} notifications "
                    f"for: {user.email}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Created: {created_count} notifications | "
                f"Skipped users: {skipped_count}"
            )
        )

