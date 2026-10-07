from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from app_portfolio.models import Portfolio
from app_riskmanage.models import RiskManagement
from app_user.models import User


class RiskManageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='r@example.com', password='pass12345', phone='09133000000'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_show_without_portfolio_returns_404(self):
        Portfolio.objects.all().delete()
        resp = self.client.get('/app/risk/')
        self.assertEqual(resp.status_code, 404)

    def test_show_creates_default(self):
        resp = self.client.get('/app/risk/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(RiskManagement.objects.filter(portfolio=self.portfolio).exists())

    def test_edit_updates_values(self):
        resp = self.client.post('/app/risk/update/', {
            'max_risk': '2', 'max_loss_daily': '5', 'max_loss_weekly': '10',
            'max_transaction_daily': '5', 'max_consecutive_loss': '3', 'min_r_r': '2',
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        rm = RiskManagement.objects.get(portfolio=self.portfolio)
        self.assertEqual(rm.max_risk, Decimal('2'))

    def test_look_returns_percentages(self):
        RiskManagement.objects.create(portfolio=self.portfolio, max_risk=2, max_loss_daily=5,
                                      max_loss_weekly=10, max_transaction_daily=5,
                                      max_consecutive_loss=3, min_r_r=2)
        resp = self.client.get('/app/risk/look/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn('max_risk_in_trade', resp.data)
