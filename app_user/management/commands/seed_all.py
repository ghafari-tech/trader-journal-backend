from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_user.models import User, Subscription
from app_transaction.models import Transaction
from app_goal.models import Goal
from app_journal.models import Journal
from app_riskmanage.models import RiskManagement
from app_notification.models import Notification


class Command(BaseCommand):
    help = "Create test data for every existing user"

    TRANSACTIONS_PER_USER = 10
    GOALS_PER_USER = 4
    JOURNALS_PER_USER = 5
    NOTIFICATIONS_PER_USER = 5

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "\nStarting per-user seed...\n"
            )
        )

        users = User.objects.all().order_by("id")

        if not users.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No users found. Create a user first."
                )
            )
            return

        self.stdout.write(
            f"Found {users.count()} users.\n"
        )

        for user in users:

            self.stdout.write(
                self.style.WARNING(
                    f"\n--- {user.email} ---"
                )
            )

            # ==================================================
            # SUBSCRIPTION
            # ==================================================

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={
                    "type": "pro",
                    "start_date": timezone.now().date(),
                    "end_date": (
                        timezone.now().date()
                        + timedelta(days=30)
                    ),
                },
            )

            if created:
                self.stdout.write(
                    "  + Subscription created"
                )
            else:
                self.stdout.write(
                    "  = Subscription already exists"
                )

            # ==================================================
            # RISK MANAGEMENT
            # ==================================================

            risk_manage, created = RiskManagement.objects.get_or_create(
                user=user,
                defaults={
                    "max_risk": 2,
                    "max_loss_daily": 5,
                    "max_loss_weekly": 10,
                    "max_transaction_daily": 5,
                    "max_consecutive_loss": 3,
                    "min_r_r": 2,
                },
            )

            if created:
                self.stdout.write(
                    "  + Risk management created"
                )
            else:
                self.stdout.write(
                    "  = Risk management already exists"
                )

            # ==================================================
            # TRANSACTIONS
            # ==================================================

            current_transactions = Transaction.objects.filter(
                user=user
            ).count()

            transactions_to_create = max(
                0,
                self.TRANSACTIONS_PER_USER - current_transactions
            )

            user_transactions = list(
                Transaction.objects.filter(
                    user=user
                ).order_by("-id")[
                    :self.TRANSACTIONS_PER_USER
                ]
            )

            if transactions_to_create > 0:

                symbols = [
                    "BTCUSDT",
                    "ETHUSDT",
                    "EURUSD",
                    "XAUUSD",
                    "AAPL",
                ]

                for i in range(transactions_to_create):

                    index = current_transactions + i + 1

                    transaction_type = (
                        "buy"
                        if index % 2
                        else "sell"
                    )

                    entry_price = (
                        Decimal("100.00000000")
                        + Decimal(index)
                    )

                    exit_price = (
                        entry_price + Decimal("5.00000000")
                        if index % 3 != 0
                        else None
                    )

                    transaction = Transaction.objects.create(
                        user=user,
                        symbol=symbols[
                            (index - 1) % len(symbols)
                        ],
                        transaction_type=transaction_type,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        volume=Decimal("0.10000000"),
                        risk_reward=Decimal("2.00"),
                        profit_loss=(
                            Decimal("25.50")
                            if index % 2
                            else Decimal("-10.25")
                        ),
                        followed_plan=index % 3 != 0,
                    )

                    user_transactions.append(transaction)

                self.stdout.write(
                    f"  + {transactions_to_create} transactions created"
                )

            else:
                self.stdout.write(
                    "  = Transactions already sufficient"
                )

            # ==================================================
            # GOALS
            # ==================================================

            current_goals = Goal.objects.filter(
                user=user
            ).count()

            goals_to_create = max(
                0,
                self.GOALS_PER_USER - current_goals
            )

            goal_types = [
                "profit",
                "risk",
                "order",
                "learning",
            ]

            for i in range(goals_to_create):

                index = current_goals + i + 1

                Goal.objects.create(
                    user=user,
                    title=f"Seed Goal {index}",
                    target_type=goal_types[
                        (index - 1) % len(goal_types)
                    ],
                    target_value=index * 10,
                    deadline=(
                        timezone.now()
                        + timedelta(days=30 + index)
                    ),
                )

            if goals_to_create > 0:
                self.stdout.write(
                    f"  + {goals_to_create} goals created"
                )
            else:
                self.stdout.write(
                    "  = Goals already sufficient"
                )

            # ==================================================
            # JOURNALS
            # ==================================================

            current_journals = Journal.objects.filter(
                user=user
            ).count()

            journals_to_create = max(
                0,
                self.JOURNALS_PER_USER - current_journals
            )

            feelings = [
                "comfort",
                "concentrated",
                "greed",
                "fear",
                "revenge",
            ]

            for i in range(journals_to_create):

                index = current_journals + i + 1

                transaction = user_transactions[
                    (index - 1) % len(user_transactions)
                ]

                Journal.objects.create(
                    user=user,
                    transaction=transaction,
                    title=f"Seed Journal {index}",
                    feel=feelings[
                        (index - 1) % len(feelings)
                    ],
                    mistakes=(
                        "Test journal entry. "
                        "No major mistake."
                    ),
                    lesson_learned=(
                        "Follow the trading plan "
                        "and manage risk."
                    ),
                    followed_plan=index % 3 != 0,
                )

            if journals_to_create > 0:
                self.stdout.write(
                    f"  + {journals_to_create} journals created"
                )
            else:
                self.stdout.write(
                    "  = Journals already sufficient"
                )

            # ==================================================
            # NOTIFICATIONS
            # ==================================================

            current_notifications = Notification.objects.filter(
                user=user
            ).count()

            notifications_to_create = max(
                0,
                self.NOTIFICATIONS_PER_USER - current_notifications
            )

            for i in range(notifications_to_create):

                index = current_notifications + i + 1

                Notification.objects.create(
                    user=user,
                    title=f"Seed Notification {index}",
                    body=(
                        "This is a test notification "
                        "generated by seed_all."
                    ),
                    icon="notification",
                    is_read=index % 3 == 0,
                    is_active=True,
                )

            if notifications_to_create > 0:
                self.stdout.write(
                    f"  + {notifications_to_create} notifications created"
                )
            else:
                self.stdout.write(
                    "  = Notifications already sufficient"
                )

        # ======================================================
        # FINAL SUMMARY
        # ======================================================

        self.stdout.write(
            self.style.SUCCESS(
                "\n========================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Per-user seed completed successfully!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "========================================\n"
            )
        )

        for user in User.objects.all().order_by("id"):

            self.stdout.write(
                f"{user.email}: "
                f"Transactions={Transaction.objects.filter(user=user).count()}, "
                f"Goals={Goal.objects.filter(user=user).count()}, "
                f"Journals={Journal.objects.filter(user=user).count()}, "
                f"Notifications={Notification.objects.filter(user=user).count()}"
            )
