from datetime import date

from django.test import TestCase

from app_setting.models import Subscription
from app_setting.serializers import UserPlanSerializer, UpdateNotificationSettingsSerializer
from app_user.models import User, UserSubscription


class SettingsSerializerTests(TestCase):
    def test_user_plan_serializer_includes_subscription_name(self):
        user = User.objects.create_user(
            email='user@example.com',
            password='password123',
            phone='09123456789',
            first_name='Test',
            last_name='User',
        )
        subscription = Subscription.objects.create(name='Pro', price=100)
        user_subscription = UserSubscription.objects.create(
            user=user,
            type=subscription,
            start_date=date.today(),
        )

        serializer = UserPlanSerializer(user_subscription)

        self.assertEqual(serializer.data['user'], user.id)
        self.assertEqual(serializer.data['type'], subscription.id)
        self.assertEqual(serializer.data['type_name'], 'Pro')

    def test_update_notification_settings_serializer_validates_input(self):
        serializer = UpdateNotificationSettingsSerializer(
            data={'field': 'add_journal_notif', 'value': True}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {'field': 'add_journal_notif', 'value': True},
        )
