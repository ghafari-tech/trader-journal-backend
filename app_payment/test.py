from datetime import timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from app_payment.models import DiscountCode, Payment
from app_setting.models import Subscription
from app_user.models import User, UserSubscription


class PaymentExtraTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='pay@example.com', password='pass12345', phone='09142000000'
        )
        self.free = Subscription.objects.create(name='Free', price=0)
        self.pro = Subscription.objects.create(name='Pro', price=250000)
        UserSubscription.objects.create(user=self.user, type=self.free)
        self.client.force_authenticate(user=self.user)

    @staticmethod
    def _gw(data):
        r = Mock()
        r.raise_for_status.return_value = None
        r.ok = True
        r.json.return_value = {'data': data}
        return r

    @patch('app_payment.views.requests.post')
    def test_discount_code_applied(self, post):
        post.return_value = self._gw({'code': 100, 'authority': 'AUTH1'})
        DiscountCode.objects.create(code='OFF50', percent=50, max_uses=5)
        resp = self.client.post(reverse('payment-request'), {
            'subscription_id': self.pro.pk, 'discount_code': 'OFF50',
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['amount'], int(self.pro.price * 10 * 0.5))

    @patch('app_payment.views.requests.post')
    def test_invalid_discount_code(self, post):
        resp = self.client.post(reverse('payment-request'), {
            'subscription_id': self.pro.pk, 'discount_code': 'NOPE',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        post.assert_not_called()

    @patch('app_payment.views.requests.post')
    def test_exhausted_discount_code(self, post):
        DiscountCode.objects.create(code='USED', percent=50, max_uses=1, used_count=1)
        resp = self.client.post(reverse('payment-request'), {
            'subscription_id': self.pro.pk, 'discount_code': 'USED',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        post.assert_not_called()

    def test_verify_missing_authority(self):
        resp = self.client.get(reverse('payment-verify'))
        self.assertEqual(resp.status_code, 400)

    @patch('app_payment.views.requests.post')
    def test_verify_creates_subscription_when_missing(self, post):
        self.user.plan.delete()
        payment = Payment.objects.create(
            authority='AUTH2', amount=1000, subscription=self.pro, user=self.user,
        )
        post.return_value = self._gw({'code': 100, 'ref_id': 'R1'})
        resp = self.client.get(reverse('payment-verify'),
                               {'Authority': 'AUTH2', 'Status': 'OK'})
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(UserSubscription.objects.filter(user=self.user, type=self.pro).exists())
