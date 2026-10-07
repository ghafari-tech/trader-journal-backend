from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from app_goal.models import Goal
from app_portfolio.models import Portfolio
from app_user.models import User


class GoalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='g@example.com', password='pass12345', phone='09130000000'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_add_goal_success(self):
        resp = self.client.post('/app/goal/add/', {
            'title': 'G1', 'target_type': 'profit', 'target_value': 100,
            'deadline': (timezone.now() + timedelta(days=10)).isoformat(),
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_add_goal_invalid_type(self):
        resp = self.client.post('/app/goal/add/', {
            'title': 'G1', 'target_type': 'wrong', 'target_value': 100,
            'deadline': (timezone.now() + timedelta(days=10)).isoformat(),
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_edit_foreign_goal_forbidden(self):
        other = User.objects.create_user(email='o@example.com', password='x', phone='09131000000')
        op = Portfolio.objects.create(user=other, name='O', broker='XM', is_active=True)
        goal = Goal.objects.create(portfolio=op, title='OG', target_type='profit',
                                   target_value=1, deadline=timezone.now() + timedelta(days=1))
        resp = self.client.post(f'/app/goal/edit/{goal.pk}/', {
            'title': 'HACK', 'target_type': 'profit', 'target_value': 1,
            'deadline': timezone.now().isoformat(),
        }, format='json')
        # Expected: 403/404, current code returns 200 and edits it
        self.assertIn(resp.status_code, (403, 404), resp.data)

    def test_delete_foreign_goal_forbidden(self):
        other = User.objects.create_user(email='o2@example.com', password='x', phone='09132000000')
        op = Portfolio.objects.create(user=other, name='O2', broker='XM', is_active=True)
        goal = Goal.objects.create(portfolio=op, title='OG2', target_type='profit',
                                   target_value=1, deadline=timezone.now() + timedelta(days=1))
        resp = self.client.delete(f'/app/goal/delete/{goal.pk}/')
        self.assertEqual(resp.status_code, 403)
