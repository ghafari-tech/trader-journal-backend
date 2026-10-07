from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from app_setting.models import Subscription
from app_user.models import User, EmailVerificationCode, UserSubscription


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free = Subscription.objects.create(name='Free', price=0)

    def _verified_user(self, email='u@example.com', password='pass12345'):
        user = User.objects.create_user(
            email=email, password=password, phone='09120000000'
        )
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return user

    # ------------------------------------------------------------------
    # register
    # ------------------------------------------------------------------
    def test_register_creates_user_and_sends_code(self):
        resp = self.client.post(reverse('signup'), {
            'first_name': 'Ali',
            'last_name': 'Ahmadi',
            'email': 'new@example.com',
            'password': 'secret123',
        }, format='json')

        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(UserSubscription.objects.filter(user__email='new@example.com').exists())

    def test_register_requires_free_subscription_to_exist(self):
        Subscription.objects.all().delete()
        resp = self.client.post(reverse('signup'), {
            'first_name': 'Ali',
            'last_name': 'Ahmadi',
            'email': 'new2@example.com',
            'password': 'secret123',
        }, format='json')
        # Expected: no crash -> but code raises Subscription.DoesNotExist
        self.assertLess(resp.status_code, 500)

    def test_register_duplicate_verified_returns_400(self):
        self._verified_user(email='dup@example.com')
        resp = self.client.post(reverse('signup'), {
            'first_name': 'A', 'last_name': 'B',
            'email': 'dup@example.com', 'password': 'secret123',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # verify register
    # ------------------------------------------------------------------
    def test_verify_register_success(self):
        user = User.objects.create_user(email='v@example.com', password='x', phone='09121111111')
        code = '123456'
        EmailVerificationCode.objects.create(
            user=user, code=code,
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        resp = self.client.post(reverse('verify-register'), {
            'email': 'v@example.com', 'code': code,
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    # ------------------------------------------------------------------
    # login / logout
    # ------------------------------------------------------------------
    def test_login_unverified_blocked(self):
        User.objects.create_user(email='nv@example.com', password='pass12345', phone='09122222222')
        resp = self.client.post(reverse('login'), {
            'email': 'nv@example.com', 'password': 'pass12345',
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_login_success_returns_tokens(self):
        self._verified_user(email='ok@example.com', password='pass12345')
        resp = self.client.post(reverse('login'), {
            'email': 'ok@example.com', 'password': 'pass12345',
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_logout_blacklists_refresh(self):
        self._verified_user(email='lo@example.com', password='pass12345')
        login = self.client.post(reverse('login'), {
            'email': 'lo@example.com', 'password': 'pass12345',
        }, format='json')
        refresh = login.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        resp = self.client.post(reverse('logout'), {'refresh': refresh}, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)

    # ------------------------------------------------------------------
    # forgot / reset password
    # ------------------------------------------------------------------
    def test_forgot_password_unknown_email_returns_404(self):
        resp = self.client.post(reverse('forgot-password'), {'email': 'nope@example.com'}, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_forgot_password_sends_code(self):
        self._verified_user(email='fp@example.com')
        resp = self.client.post(reverse('forgot-password'), {'email': 'fp@example.com'}, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_success(self):
        user = self._verified_user(email='rp@example.com')
        code = '654321'
        EmailVerificationCode.objects.create(
            user=user, code=code, expires_at=timezone.now() + timedelta(minutes=5)
        )
        resp = self.client.post(reverse('reset-password'), {
            'email': 'rp@example.com', 'code': code, 'new_password': 'brandnew1',
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        user.refresh_from_db()
        self.assertTrue(user.check_password('brandnew1'))
