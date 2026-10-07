from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from app_user.models import User


class DashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='d@example.com', password='pass12345', phone='09136000000'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def _tx(self, pnl):
        return Transaction.objects.create(
            portfolio=self.portfolio, symbol='EURUSD', transaction_type='buy',
            entry_price=Decimal('1.1'), exit_price=Decimal('1.2'),
            volume=Decimal('0.1'), profit_loss=Decimal(str(pnl)),
        )

    def test_summary_no_portfolio(self):
        Portfolio.objects.all().delete()
        resp = self.client.get('/app/dashboard/summery/')
        self.assertEqual(resp.status_code, 404)

    def test_summary_stats(self):
        self._tx(100)
        self._tx(-50)
        resp = self.client.get('/app/dashboard/summery/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data['total_trades'], 2)
        self.assertEqual(resp.data['winning_trades'], 1)
        self.assertEqual(resp.data['losing_trades'], 1)

    def test_equity_chart(self):
        resp = self.client.get('/app/dashboard/equity/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data['data']), 30)

    def test_win_loss_rate(self):
        self._tx(100)
        resp = self.client.get('/app/dashboard/win-loss-rate/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data['total_trades'], 1)

    def test_monthly_performance(self):
        resp = self.client.get('/app/dashboard/monthly-performance/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data['months']), 12)

    def test_drawdown(self):
        self._tx(100)
        self._tx(-50)
        resp = self.client.get('/app/dashboard/drawdown/')
        self.assertEqual(resp.status_code, 200, resp.data)
