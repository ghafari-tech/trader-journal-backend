from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from app_ai_analysis.models import AIModel, AIAnalysis, AIAnalysisRequest
from app_ai_analysis.views import _resolve_plan
from app_portfolio.models import Portfolio
from app_setting.models import Subscription
from app_user.models import User, UserSubscription


class AIAnalysisTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free = Subscription.objects.create(name='Free', price=0)
        self.user = User.objects.create_user(
            email='ai@example.com', password='pass12345', phone='09141000000'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='P', broker='XM', balance=Decimal('1000.00'), is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_models_list(self):
        AIModel.objects.create(name='M', model='gemini', description='d', api_key='k', is_default=True)
        resp = self.client.get('/app/ai-coach/models/')
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_ai_analysis_no_portfolio(self):
        Portfolio.objects.all().delete()
        resp = self.client.get('/app/ai-coach/')
        self.assertEqual(resp.status_code, 404)

    def test_ai_analysis_no_default_model(self):
        resp = self.client.get('/app/ai-coach/')
        self.assertEqual(resp.status_code, 400)

    def test_resolve_plan_free_when_no_subscription(self):
        self.assertEqual(_resolve_plan(self.user), 'free')

    def test_resolve_plan_pro_by_name(self):
        pro = Subscription.objects.create(name='Pro', price=100)
        UserSubscription.objects.create(user=self.user, type=pro)
        self.assertEqual(_resolve_plan(self.user), 'pro')

    def test_regenerate_enforces_daily_limit(self):
        model = AIModel.objects.create(name='M', model='gemini', description='d', api_key='k', is_default=True)
        UserSubscription.objects.create(user=self.user, type=self.free)
        # free plan -> limit 1; simulate one already used today
        AIAnalysisRequest.objects.create(user=self.user, portfolio=self.portfolio, model_used=model)
        resp = self.client.post('/app/ai-coach/regenerate/', {}, format='json')
        self.assertEqual(resp.status_code, 429, resp.data)
