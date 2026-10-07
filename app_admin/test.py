from django.test import TestCase
from rest_framework.test import APIClient

from app_setting.models import Subscription
from app_user.models import User, UserSubscription


class AdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free = Subscription.objects.create(name='Free', price=0)
        self.pro = Subscription.objects.create(name='Pro', price=250000)
        self.admin = User.objects.create_user(
            email='admin@example.com', password='pass12345', phone='09137000000'
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.normal = User.objects.create_user(
            email='normal@example.com', password='pass12345', phone='09138000000'
        )

    def test_users_list_requires_admin(self):
        self.client.force_authenticate(user=self.normal)
        resp = self.client.get('/app/admin/users/')
        self.assertEqual(resp.status_code, 403)

    def test_users_list_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/app/admin/users/')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_subscriptions_list_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/app/admin/subscriptions/')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_update_subscription_requires_admin(self):
        self.client.force_authenticate(user=self.normal)
        resp = self.client.patch(f'/app/admin/subscriptions/update/{self.pro.pk}/',
                                 {'price': 1}, format='json')
        # Expected 403 for a non-admin, code only checks IsAuthenticated
        self.assertEqual(resp.status_code, 403, resp.data)
