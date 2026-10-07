from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from app_journal.models import Journal
from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from app_user.models import User


class JournalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='j@example.com', password='pass12345', phone='09128000000'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def _payload(self, **kw):
        data = {'title': 'J1', 'feel': 'comfort', 'mistakes': 'none',
                'lesson_learned': 'keep going', 'followed_plan': True}
        data.update(kw)
        return data

    def test_list_without_portfolio_returns_404(self):
        Portfolio.objects.all().delete()
        resp = self.client.get('/app/journal/')
        self.assertEqual(resp.status_code, 404)

    def test_add_journal_success(self):
        resp = self.client.post('/app/journal/add/', self._payload(), format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(Journal.objects.filter(title='J1').exists())

    def test_add_journal_rejects_invalid_feel(self):
        resp = self.client.post('/app/journal/add/', self._payload(feel='happy'), format='json')
        self.assertEqual(resp.status_code, 400)

    def test_add_journal_followed_plan_false_is_accepted(self):
        # followed_plan=False is a valid value and must be accepted
        resp = self.client.post('/app/journal/add/', self._payload(followed_plan=False), format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        journal = Journal.objects.get(title='J1')
        self.assertFalse(journal.followed_plan)

    def test_add_journal_with_invalid_transaction_prefix(self):
        resp = self.client.post('/app/journal/add/', self._payload(transaction_id='X-1'), format='json')
        self.assertEqual(resp.status_code, 400)

    def test_add_journal_with_foreign_transaction_rejected(self):
        other = User.objects.create_user(email='o@example.com', password='x', phone='09129000000')
        op = Portfolio.objects.create(user=other, name='O', broker='XM', is_active=True)
        t = Transaction.objects.create(portfolio=op, symbol='EURUSD', transaction_type='buy',
                                       entry_price=Decimal('1.1'), volume=Decimal('0.1'))
        resp = self.client.post('/app/journal/add/', self._payload(transaction_id=t.transaction_id), format='json')
        self.assertEqual(resp.status_code, 400)
