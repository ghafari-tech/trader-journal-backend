from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import Mock, patch

from app_setting.models import Subscription
from app_user.models import User, UserSubscription
from .models import Payment


class PaymentApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			email='trader@example.com',
			password='test-password',
			image_profile='profiles/trader.jpg',
			phone='09123456789',
		)
		self.free_subscription = Subscription.objects.create(
			name='Free',
			price=0,
		)
		self.paid_subscription = Subscription.objects.create(
			name='Pro',
			price=250000,
		)
		today = timezone.localdate()
		self.active_plan_end = today + timezone.timedelta(days=5)
		self.user_subscription = UserSubscription.objects.create(
			user=self.user,
			type=self.free_subscription,
			start_date=today - timezone.timedelta(days=10),
			end_date=self.active_plan_end,
		)
		self.client.force_authenticate(user=self.user)

	@staticmethod
	def gateway_response(data):
		response = Mock()
		response.raise_for_status.return_value = None
		response.json.return_value = {'data': data}
		return response

	@patch('app_payment.views.requests.post')
	def test_request_creates_payment_and_returns_start_url(self, post):
		post.return_value = self.gateway_response({
			'code': 100,
			'authority': 'A00000000000000000000000000123456789',
		})

		response = self.client.post(
			reverse('payment-request'),
			{'subscription_id': self.paid_subscription.pk},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		self.assertIn('A00000000000000000000000000123456789', response.data['payment_url'])
		payment = Payment.objects.get(authority=response.data['authority'])
		self.assertEqual(payment.amount, self.paid_subscription.price * 10)
		self.assertFalse(payment.is_paid)
		self.assertEqual(post.call_args.kwargs['json']['amount'], payment.amount)

	@patch('app_payment.views.requests.post')
	def test_invalid_subscription_does_not_call_gateway(self, post):
		response = self.client.post(
			reverse('payment-request'),
			{'subscription_id': 999999},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		post.assert_not_called()

	@patch('app_payment.views.requests.post')
	def test_unverified_callback_does_not_change_subscription(self, post):
		payment = Payment.objects.create(
			authority='unverified-authority',
			amount=self.paid_subscription.price * 10,
			subscription=self.paid_subscription,
			user=self.user,
		)
		post.return_value = self.gateway_response({'code': -9})

		response = self.client.get(
			reverse('payment-verify'),
			{'Authority': payment.authority, 'Status': 'OK'},
		)

		self.assertEqual(response.status_code, 400)
		self.user_subscription.refresh_from_db()
		payment.refresh_from_db()
		self.assertEqual(self.user_subscription.type, self.free_subscription)
		self.assertEqual(self.user_subscription.end_date, self.active_plan_end)
		self.assertFalse(payment.is_paid)

	@patch('app_payment.views.requests.post')
	def test_verified_callback_changes_plan_and_extends_active_period(self, post):
		payment = Payment.objects.create(
			authority='verified-authority',
			amount=self.paid_subscription.price * 10,
			subscription=self.paid_subscription,
			user=self.user,
		)
		post.return_value = self.gateway_response({
			'code': 100,
			'ref_id': '123456789',
		})

		response = self.client.get(
			reverse('payment-verify'),
			{'Authority': payment.authority, 'Status': 'OK'},
		)

		self.assertEqual(response.status_code, 200)
		self.user_subscription.refresh_from_db()
		payment.refresh_from_db()
		self.assertEqual(self.user_subscription.type, self.paid_subscription)
		self.assertEqual(
			self.user_subscription.end_date,
			self.active_plan_end + timezone.timedelta(days=30),
		)
		self.assertTrue(payment.is_paid)
		self.assertEqual(payment.ref_id, '123456789')
		self.assertEqual(post.call_args.kwargs['json']['amount'], payment.amount)

	@patch('app_payment.views.requests.post')
	def test_duplicate_callback_does_not_extend_period_twice(self, post):
		payment = Payment.objects.create(
			authority='duplicate-authority',
			amount=self.paid_subscription.price * 10,
			subscription=self.paid_subscription,
			user=self.user,
		)
		post.return_value = self.gateway_response({
			'code': 100,
			'ref_id': '987654321',
		})
		callback = reverse('payment-verify')
		params = {'Authority': payment.authority, 'Status': 'OK'}

		first_response = self.client.get(callback, params)
		first_end_date = UserSubscription.objects.get(user=self.user).end_date
		second_response = self.client.get(callback, params)

		self.assertEqual(first_response.status_code, 200)
		self.assertEqual(second_response.data['code'], 'ALREADY_VERIFIED')
		self.assertEqual(UserSubscription.objects.get(user=self.user).end_date, first_end_date)
		self.assertEqual(post.call_count, 1)
