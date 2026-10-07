from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from app_setting.models import Subscription
from app_user.models import User, UserSubscription


class SettingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free = Subscription.objects.create(name='Free', price=0)
        self.pro = Subscription.objects.create(name='Pro', price=250000)
        self.user = User.objects.create_user(
            email='s@example.com', password='pass12345', phone='09123000000'
        )
        self.user.is_verified = True
        self.user.save(update_fields=['is_verified'])
        self.client.force_authenticate(user=self.user)

    def test_user_info(self):
        resp = self.client.get('/app/settings/user-info/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data['email'], 's@example.com')

    def test_update_user_info_email_conflict(self):
        other = User.objects.create_user(email='other@example.com', password='x', phone='09124000000')
        resp = self.client.patch('/app/settings/update/', {'email': 'other@example.com'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_user_plan_info_without_existing_plan(self):
        # No UserSubscription exists -> code tries to create without type (required FK)
        resp = self.client.get('/app/settings/plan/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn('plan', resp.data)

    def test_plan_list_returns_all_plans(self):
        resp = self.client.get('/app/settings/plans/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data['plans']), 2)

    def test_notification_settings_default(self):
        resp = self.client.get('/app/settings/notification/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn('risk_up_warning_notif', resp.data)

    def test_update_notification_setting(self):
        resp = self.client.patch('/app/settings/notification/update/', {
            'field': 'fomo_notif', 'value': True,
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_metatrader_status_without_portfolio_returns_404(self):
        # No active portfolio -> should return 404, not crash
        resp = self.client.get('/app/settings/metatrader/mt-status/')
        self.assertEqual(resp.status_code, 404, resp.data)
