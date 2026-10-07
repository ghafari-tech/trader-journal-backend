import json
from django.db import transaction
from drf_spectacular.utils import extend_schema
from google import genai
from google.genai import types

from .serializers import *
from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from app_user.models import UserSubscription


def call_ai_model(ai_model, prompt):
    if not ai_model.url:
        raise ValueError("AI service URL is not configured.")
    if not ai_model.api_key:
        raise ValueError("API key is not configured.")

    client = genai.Client(
        api_key=ai_model.api_key,
        http_options={"baseUrl": ai_model.url.rstrip("/")}
    )

    response = client.models.generate_content(
        model=ai_model.model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        )
    )

    text_content = (response.text or "").strip()

    if text_content.startswith("```"):
        text_content = text_content.split("```")[1]
        if text_content.startswith("json"):
            text_content = text_content[4:]
        text_content = text_content.strip()

    return json.loads(text_content)


def generate_and_save_ai_analysis(portfolio, ai_model=None):
    if ai_model is None:
        ai_model = AIModel.objects.filter(is_default=True).first() or AIModel.objects.first()

    if not ai_model:
        raise ValueError("No AI model found.")

    recent_trades = Transaction.objects.filter(
        portfolio=portfolio,
        closed_at__isnull=False
    ).order_by('-closed_at')[:50]

    trades_data = [
        {
            "ticket": t.transaction_id,
            "symbol": t.symbol,
            "type": t.transaction_type,
            "profit_loss": float(t.profit_loss) if t.profit_loss else 0,
            "r_r": float(t.r_r) if t.r_r else 0,
            "followed_plan": t.followed_plan
        }
        for t in recent_trades
    ]

    if not trades_data:
        ai_response = {
            "weekly_report": (
                "هنوز معامله‌ای برای تحلیل ثبت نکرده‌اید. "
                "برای دریافت گزارش هوشمند، اولین معاملات خود را در ژورنال ثبت کنید."
            ),
            "trading_regime": 0,
            "capital_management": 0,
            "psychology": 0,
            "adherence_to_the_plan": 0,
            "strengths": [],
            "weaknesses": [],
            "performance_days": [],
            "performance_weeks": [],
            "suggested_exercises": [
                {
                    "text": (
                        "امروز اولین معامله خود را همراه با دلیل ورود، "
                        "حد ضرر و حد سود در ژورنال ثبت کنید."
                    )
                }
            ],
        }
    else:
        prompt = f"""
            You are a professional trading analyst. Based on the closed trade data below, 
            provide a complete analysis.
            Return ONLY valid JSON. Do NOT write any text outside the JSON.

            ================ LANGUAGE RULES (STRICT) ================
            1) ALL human-readable text values MUST be written in Persian (Farsi):
            - weekly_report
            - strengths[].title, strengths[].maintaining_sustainability
            - weaknesses[].title, weaknesses[].solution
            - performance_days[].description, performance_days[].golden_window
            - performance_weeks[].description, performance_weeks[].golden_window
            - suggested_exercises[].text

            2) NUMERIC fields MUST remain raw numbers (NO strings, NO Persian digits):
            - trading_regime, capital_management, psychology, adherence_to_the_plan
            - transaction_count, net_profit, win_rate
            Example: 75  (correct)  /  "۷۵"  (WRONG)

            3) DATE fields MUST stay in Gregorian "YYYY-MM-DD" format:
            - date, week_start_date, week_end_date
            Example: "2026-10-04"  (correct)  /  "۱۴۰۵/۰۷/۱۲"  (WRONG)

            4) Trading symbols in best_trade / worst_trade MUST stay in original Latin
            form (e.g. "EURUSD", "XAUUSD", "BTCUSD"). You may optionally append a
            short Persian label in parentheses, e.g. "EURUSD (یورو/دلار)".
            Do NOT translate the symbol itself.

            5) JSON keys MUST remain exactly in English as shown in the template below.
            =========================================================

            Closed trade data:
            {json.dumps(trades_data, ensure_ascii=False, indent=2)}

            Required JSON structure:
            {{
            "weekly_report": "گزارش هفتگی به فارسی",
            "trading_regime": integer between 0 and 100,
            "capital_management": integer between 0 and 100,
            "psychology": integer between 0 and 100,
            "adherence_to_the_plan": integer between 0 and 100,
            "strengths": [
                {{
                "title": "عنوان نقطه قوت به فارسی",
                "maintaining_sustainability": "روش حفظ این نقطه قوت به فارسی"
                }}
            ],
            "weaknesses": [
                {{
                "title": "عنوان نقطه ضعف به فارسی",
                "solution": "راه‌حل پیشنهادی به فارسی"
                }}
            ],
            "performance_days": [
                {{
                "date": "YYYY-MM-DD",
                "description": "توضیح عملکرد آن روز به فارسی",
                "transaction_count": integer,
                "net_profit": float,
                "win_rate": float between 0 and 100,
                "adherence_to_the_plan": float between 0 and 100,
                "best_trade": "EURUSD",
                "worst_trade": "GBPUSD",
                "golden_window": "بازه طلایی معاملات آن روز به فارسی"
                }}
            ],
            "performance_weeks": [
                {{
                "week_start_date": "YYYY-MM-DD",
                "week_end_date": "YYYY-MM-DD",
                "description": "توضیح عملکرد هفته به فارسی",
                "transaction_count": integer,
                "net_profit": float,
                "win_rate": float between 0 and 100,
                "adherence_to_the_plan": float between 0 and 100,
                "best_trade": "EURUSD",
                "worst_trade": "GBPUSD",
                "golden_window": "بازه طلایی معاملات آن هفته به فارسی"
                }}
            ],
            "suggested_exercises": [
                {{ "text": "متن تمرین پیشنهادی به فارسی" }}
            ]
            }}

            Final reminder:
            - Persian for all text.
            - Numbers stay numbers.
            - Dates stay YYYY-MM-DD.
            - Symbols stay in Latin.
            - JSON keys stay in English.
        """
        ai_response = call_ai_model(ai_model, prompt)

    with transaction.atomic():
        analysis = AIAnalysis.objects.create(
            portfolio=portfolio,
            model=ai_model,
            weekly_report=ai_response.get("weekly_report", ""),
            trading_regime=ai_response.get("trading_regime", 0),
            capital_management=ai_response.get("capital_management", 0),
            psychology=ai_response.get("psychology", 0),
            adherence_to_the_plan=ai_response.get("adherence_to_the_plan", 0)
        )

        for strength in ai_response.get("strengths", []):
            Strengths.objects.create(
                analysis=analysis,
                title=strength.get("title", ""),
                maintaining_sustainability=strength.get("maintaining_sustainability", "")
            )

        for weakness in ai_response.get("weaknesses", []):
            Weaknesses.objects.create(
                analysis=analysis,
                title=weakness.get("title", ""),
                solution=weakness.get("solution", "")
            )

        for day_report in ai_response.get("performance_days", []):
            PerformanceReportDay.objects.create(
                analysis=analysis,
                date=day_report.get("date"),
                description=day_report.get("description", ""),
                transaction_count=day_report.get("transaction_count", 0),
                net_profit=day_report.get("net_profit", 0),
                win_rate=day_report.get("win_rate", 0),
                adherence_to_the_plan=day_report.get("adherence_to_the_plan", 0),
                best_trade=day_report.get("best_trade", ""),
                worst_trade=day_report.get("worst_trade", ""),
                golden_window=day_report.get("golden_window", "")
            )

        for week_report in ai_response.get("performance_weeks", []):
            PerformanceReportWeek.objects.create(
                analysis=analysis,
                week_start_date=week_report.get("week_start_date"),
                week_end_date=week_report.get("week_end_date"),
                description=week_report.get("description", ""),
                transaction_count=week_report.get("transaction_count", 0),
                net_profit=week_report.get("net_profit", 0),
                win_rate=week_report.get("win_rate", 0),
                adherence_to_the_plan=week_report.get("adherence_to_the_plan", 0),
                best_trade=week_report.get("best_trade", ""),
                worst_trade=week_report.get("worst_trade", ""),
                golden_window=week_report.get("golden_window", "")
            )

        for exercise in ai_response.get("suggested_exercises", []):
            SuggestedExercises.objects.create(
                analysis=analysis,
                text=exercise.get("text", "")
            )

    return analysis


PLAN_DAILY_LIMITS = {
    "free": 1,
    "pro": 3,
    "pro_max": 10,
}


def _resolve_plan(user):
    try:
        sub = user.plan
    except UserSubscription.DoesNotExist:
        return "free"

    today = timezone.now().date()
    if sub.end_date and sub.end_date < today:
        return "free"

    subscription = sub.type
    name = (getattr(subscription, "name", "") or "").lower()

    if "max" in name:
        return "pro_max"
    if "pro" in name:
        return "pro"
    return "free"


@extend_schema(tags=["AI Analysis"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_analysis_view(request):
    portfolio = Portfolio.objects.filter(user=request.user, is_active=True).first()
    if not portfolio:
        return Response({"error": "No active portfolio found."}, status=404)

    analysis = AIAnalysis.objects.filter(portfolio=portfolio).order_by("-date").first()
    if analysis:
        return Response(AIAnalysisSerializer(analysis).data, status=200)

    try:
        default_model = AIModel.objects.filter(is_default=True).first()
        if not default_model:
            return Response({"error": "Default AI model not found."}, status=400)

        with transaction.atomic():
            AIAnalysisRequest.objects.create(
                user=request.user,
                portfolio=portfolio,
                model_used=default_model,
            )
            analysis = generate_and_save_ai_analysis(portfolio, ai_model=default_model)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response(AIAnalysisSerializer(analysis).data, status=201)


@extend_schema(tags=["AI Analysis"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_models_list_view(request):
    models = AIModel.objects.all().values(
        "id", "name", "model", "description", "is_default"
    )
    return Response(list(models), status=200)


@extend_schema(tags=["AI Analysis"], request=RegenerateAIAnalysisRequestSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def regenerate_ai_analysis_view(request):
    portfolio = Portfolio.objects.filter(user=request.user, is_active=True).first()
    if not portfolio:
        return Response({"error": "No active portfolio found."}, status=404)

    plan = _resolve_plan(request.user)
    daily_limit = PLAN_DAILY_LIMITS.get(plan, 1)

    today = timezone.now().date()
    used_today = AIAnalysisRequest.objects.filter(
        portfolio=portfolio,
        created_at__date=today,
    ).count()

    if used_today >= daily_limit:
        return Response(
            {
                "error": "Your daily quota has been exhausted.",
                "plan": plan,
                "limit": daily_limit,
                "used": used_today,
            },
            status=429,
        )

    model_id = request.data.get("model_id") or request.data.get("models_id")
    if model_id:
        ai_model = AIModel.objects.filter(id=model_id).first()
        if not ai_model:
            return Response({"error": "Selected model not found."}, status=404)
    else:
        ai_model = AIModel.objects.filter(is_default=True).first()
        if not ai_model:
            return Response({"error": "Default AI model not found."}, status=400)

    try:
        with transaction.atomic():
            AIAnalysis.objects.filter(portfolio=portfolio).delete()
            AIAnalysisRequest.objects.create(
                user=request.user,
                portfolio=portfolio,
                model_used=ai_model,
            )
            analysis = generate_and_save_ai_analysis(portfolio, ai_model=ai_model)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response(
        {
            "message": "AI analysis regenerated successfully.",
            "plan": plan,
            "limit": daily_limit,
            "used": used_today + 1,
        },
        status=201,
    )