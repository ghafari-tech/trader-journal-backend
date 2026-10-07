from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from app_badge.models import Badge, UserBadge
from app_badge.services import unlock, unlock_streak
from app_portfolio.models import Portfolio
from app_transaction.models import MetaTraderAccount, Transaction
from app_user.models import User


class BadgeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='b@example.com', password='pass12345', phone='09139000000'
        )
        self.admin = User.objects.create_user(
            email='ba@example.com', password='pass12345', phone='09140000000'
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )

    def test_badge_list_requires_auth(self):
        resp = self.client.get('/app/achievements/list/')
        self.assertEqual(resp.status_code, 401)

    def test_add_badge_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/app/achievements/add/', {
            'name': 'X', 'description': 'd', 'trigger_type': 'first_trade',
            'trigger_count': 1, 'order': 1,
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_add_badge_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post('/app/achievements/add/', {
            'name': 'X', 'description': 'd', 'trigger_type': 'first_trade',
            'trigger_count': 1, 'order': 1,
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)

    def test_unlock_service_finishes_badge(self):
        badge = Badge.objects.create(name='FT', description='d', trigger_type='first_trade', trigger_count=1)
        unlocked = unlock(self.user, 'first_trade')
        self.assertIn(badge, unlocked)
        self.assertTrue(UserBadge.objects.get(user=self.user, badge=badge).is_finished)

    def test_signal_unlocks_first_trade(self):
        badge = Badge.objects.create(name='FT', description='d', trigger_type='first_trade', trigger_count=1)
        Transaction.objects.create(
            portfolio=self.portfolio, symbol='EURUSD', transaction_type='buy',
            entry_price=Decimal('1.1'), volume=Decimal('0.1'),
        )
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=badge, is_finished=True).exists())

    def test_streak_requires_consecutive_days(self):
        badge = Badge.objects.create(name='JS', description='d', trigger_type='journal_streak', trigger_count=2)
        unlock_streak(self.user, 'journal_streak')
        ub = UserBadge.objects.get(user=self.user, badge=badge)
        self.assertEqual(ub.progress, 1)
        self.assertFalse(ub.is_finished)
