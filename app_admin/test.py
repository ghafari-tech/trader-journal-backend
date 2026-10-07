from django.test import TestCase
from rest_framework.test import APIClient

from app_ai_analysis.models import AIModel
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
        self.assertEqual(resp.status_code, 403, resp.data)

    # ------------------------------------------------------------------
    # AI models
    # ------------------------------------------------------------------
    def test_ai_models_list_requires_admin(self):
        self.client.force_authenticate(user=self.normal)
        resp = self.client.get('/app/admin/ai-models/')
        self.assertEqual(resp.status_code, 403)

    def test_ai_models_list_returns_all_fields(self):
        AIModel.objects.create(
            name='Gemini', model='gemini-2.0', description='d',
            api_key='key', url='https://example.com', is_default=True,
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/app/admin/ai-models/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data['ai_models']), 1)
        item = resp.data['ai_models'][0]
        for field in ['id', 'name', 'model', 'description', 'api_key',
                      'url', 'is_default', 'used_tokens']:
            self.assertIn(field, item)

    def test_ai_model_create_requires_admin(self):
        self.client.force_authenticate(user=self.normal)
        resp = self.client.post('/app/admin/ai-models/add/', {
            'name': 'X', 'model': 'g', 'description': 'd', 'api_key': 'k',
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_ai_model_create(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post('/app/admin/ai-models/add/', {
            'name': 'X', 'model': 'g', 'description': 'd',
            'api_key': 'k', 'url': 'https://example.com', 'is_default': True,
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertTrue(AIModel.objects.filter(name='X').exists())
