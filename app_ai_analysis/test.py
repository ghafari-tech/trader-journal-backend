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

    def test_call_ai_model_accumulates_used_tokens(self):
        from unittest.mock import MagicMock, patch
        from app_ai_analysis.views import call_ai_model

        model = AIModel.objects.create(
            name='M', model='gemini', description='d',
            api_key='k', url='https://example.com', is_default=True,
        )

        fake_response = MagicMock()
        fake_response.text = '{"weekly_report": "ok"}'
        fake_response.usage_metadata.total_token_count = 123

        fake_client = MagicMock()
        fake_client.models.generate_content.return_value = fake_response

        with patch('app_ai_analysis.views.genai.Client', return_value=fake_client):
            call_ai_model(model, 'prompt')

        model.refresh_from_db()
        self.assertEqual(model.used_tokens, 123)

    def test_call_ai_model_falls_back_to_prompt_plus_candidates(self):
        from unittest.mock import MagicMock, patch
        from app_ai_analysis.views import call_ai_model

        model = AIModel.objects.create(
            name='M', model='gemini', description='d',
            api_key='k', url='https://example.com', is_default=True,
        )

        fake_response = MagicMock()
        fake_response.text = '{"weekly_report": "ok"}'
        fake_response.usage_metadata.total_token_count = 0
        fake_response.usage_metadata.prompt_token_count = 40
        fake_response.usage_metadata.candidates_token_count = 60

        fake_client = MagicMock()
        fake_client.models.generate_content.return_value = fake_response

        with patch('app_ai_analysis.views.genai.Client', return_value=fake_client):
            call_ai_model(model, 'prompt')

        model.refresh_from_db()
        self.assertEqual(model.used_tokens, 100)

    def test_call_ai_model_charges_the_selected_model_only(self):
        from unittest.mock import MagicMock, patch
        from app_ai_analysis.views import call_ai_model

        selected = AIModel.objects.create(
            name='Selected', model='gemini', description='d',
            api_key='k', url='https://example.com', is_default=False,
        )
        default = AIModel.objects.create(
            name='Default', model='gemini', description='d',
            api_key='k', url='https://example.com', is_default=True,
        )

        fake_response = MagicMock()
        fake_response.text = '{"weekly_report": "ok"}'
        fake_response.usage_metadata.total_token_count = 77

        fake_client = MagicMock()
        fake_client.models.generate_content.return_value = fake_response

        with patch('app_ai_analysis.views.genai.Client', return_value=fake_client):
            call_ai_model(selected, 'prompt')

        selected.refresh_from_db()
        default.refresh_from_db()
        self.assertEqual(selected.used_tokens, 77)
        self.assertEqual(default.used_tokens, 0)

    def test_regenerate_enforces_daily_limit(self):
        model = AIModel.objects.create(name='M', model='gemini', description='d', api_key='k', is_default=True)
        UserSubscription.objects.create(user=self.user, type=self.free)
        # free plan -> limit 1; simulate one already used today
        AIAnalysisRequest.objects.create(user=self.user, portfolio=self.portfolio, model_used=model)
        resp = self.client.post('/app/ai-coach/regenerate/', {}, format='json')
        self.assertEqual(resp.status_code, 429, resp.data)
