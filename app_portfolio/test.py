from django.test import TestCase
from rest_framework.test import APIClient

from app_portfolio.models import Portfolio
from app_user.models import User


class PortfolioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='p@example.com', password='pass12345', phone='09125000000'
        )
        self.user.is_verified = True
        self.user.save(update_fields=['is_verified'])
        self.client.force_authenticate(user=self.user)

    def _create(self, name='P1', **kw):
        data = {'name': name, 'broker': 'XM', 'balance': '1000.00',
                'currency': 'USD', 'leverage': '1:100'}
        data.update(kw)
        return self.client.post('/app/portfolio/add/', data, format='json')

    def test_create_first_portfolio_is_active(self):
        resp = self._create()
        self.assertEqual(resp.status_code, 201, resp.data)
        p = Portfolio.objects.get(name='P1')
        self.assertTrue(p.is_active)

    def test_only_one_active_portfolio(self):
        self._create('P1')
        self._create('P2')
        self.assertEqual(Portfolio.objects.filter(user=self.user, is_active=True).count(), 1)

    def test_list_excludes_archived(self):
        self._create('P1')
        p = Portfolio.objects.get(name='P1')
        p.is_archived = True
        p.save()
        resp = self.client.get('/app/portfolio/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['portfolios']), 0)

    def test_edit_portfolio(self):
        self._create('P1')
        p = Portfolio.objects.get(name='P1')
        resp = self.client.put(f'/app/portfolio/edit/{p.pk}/', {
            'name': 'P1-edit', 'broker': 'XM', 'balance': '2000.00',
            'currency': 'USD', 'leverage': '1:100',
        }, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_delete_active_portfolio_activates_another(self):
        self._create('P1')
        self._create('P2')
        p1 = Portfolio.objects.get(name='P1')
        resp = self.client.delete(f'/app/portfolio/delete/{p1.pk}/')
        self.assertEqual(resp.status_code, 200, resp.data)
        # Some portfolio should remain active
        self.assertTrue(Portfolio.objects.filter(user=self.user, is_active=True).exists())

    def test_archive_active_portfolio_moves_active_flag(self):
        self._create('P1')
        self._create('P2')
        active = Portfolio.objects.get(user=self.user, is_active=True)
        resp = self.client.patch(f'/app/portfolio/archive/{active.pk}/')
        self.assertEqual(resp.status_code, 200, resp.data)
        active.refresh_from_db()
        # The archived portfolio must NOT stay active
        self.assertFalse(active.is_active)

    def test_archive_out_restores(self):
        self._create('P1')
        p = Portfolio.objects.get(name='P1')
        self.client.patch(f'/app/portfolio/archive/{p.pk}/')
        resp = self.client.patch(f'/app/portfolio/archive-out/{p.pk}/')
        self.assertEqual(resp.status_code, 201, resp.data)
        p.refresh_from_db()
        self.assertFalse(p.is_archived)

    def test_cannot_access_other_users_portfolio(self):
        self._create('P1')
        p = Portfolio.objects.get(name='P1')
        other = User.objects.create_user(email='o@example.com', password='x', phone='09126000000')
        self.client.force_authenticate(user=other)
        resp = self.client.delete(f'/app/portfolio/delete/{p.pk}/')
        self.assertEqual(resp.status_code, 404)
