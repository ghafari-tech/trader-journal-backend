import json
from django.db import transaction
from drf_spectacular.utils import extend_schema
from google import genai
from google.genai import types

from app_ai_analysis.serializers import AIAnalysisSerializer
from app_portfolio.models import Portfolio
from app_transaction.models import Transaction
from .models import (
    AIModel, AIAnalysis, Strengths, Weaknesses,
    PerformanceReportDay, PerformanceReportWeek, SuggestedExercises
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def call_ai_model(ai_model, prompt):
    if not ai_model.url:
        raise ValueError("آدرس سرویس هوش مصنوعی تنظیم نشده است.")
    if not ai_model.api_key:
        raise ValueError("کلید API تنظیم نشده است.")

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
        raise ValueError("مدل هوش مصنوعی یافت نشد.")

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
            "weekly_report": "هنوز معامله‌ای برای تحلیل ثبت نکرده‌ای. برای دریافت گزارش هوشمند، اولین معاملاتت را در ژورنال ثبت کن.",
            "trading_regime": 0,
            "capital_management": 0,
            "psychology": 0,
            "adherence_to_the_plan": 0,
            "strengths": [],
            "weaknesses": [],
            "performance_days": [],
            "performance_weeks": [],
            "suggested_exercises": [
                {"text": "امروز اولین معامله‌ات را با ثبت دلیل ورود، حد ضرر و حد سود در ژورنال ثبت کن."}
            ]
        }
    else:
        prompt = f"""
تو یک تحلیلگر معاملاتی حرفه‌ای هستی. بر اساس داده‌های معاملات بسته‌شده‌ی زیر، یک تحلیل کامل به زبان فارسی ارائه بده.
خروجی را دقیقاً به صورت یک JSON معتبر برگردان. هیچ متن اضافه‌ای بیرون از JSON ننویس.

داده‌های معاملات بسته‌شده:
{json.dumps(trades_data, ensure_ascii=False, indent=2)}

ساختار JSON مورد نیاز:
{{
  "weekly_report": "متن گزارش هفتگی به فارسی",
  "trading_regime": عدد صحیح بین ۰ تا ۱۰۰,
  "capital_management": عدد صحیح بین ۰ تا ۱۰۰,
  "psychology": عدد صحیح بین ۰ تا ۱۰۰,
  "adherence_to_the_plan": عدد صحیح بین ۰ تا ۱۰۰,
  "strengths": [
    {{
      "title": "عنوان نقطه قوت",
      "maintaining_sustainability": "راهکار حفظ و تداوم این نقطه قوت"
    }}
  ],
  "weaknesses": [
    {{
      "title": "عنوان نقطه ضعف",
      "solution": "راهکار پیشنهادی برای رفع این نقطه ضعف"
    }}
  ],
  "performance_days": [
    {{
      "date": "تاریخ به فرمت YYYY-MM-DD",
      "description": "توضیح عملکرد آن روز",
      "transaction_count": عدد صحیح,
      "net_profit": عدد اعشاری,
      "win_rate": عدد اعشاری بین ۰ تا ۱۰۰,
      "adherence_to_the_plan": عدد اعشاری بین ۰ تا ۱۰۰,
      "best_trade": "نام نماد بهترین معامله",
      "worst_trade": "نام نماد بدترین معامله",
      "golden_window": "بازه‌ی زمانی طلایی معاملات آن روز"
    }}
  ],
  "performance_weeks": [
    {{
      "week_start_date": "تاریخ شروع هفته به فرمت YYYY-MM-DD",
      "week_end_date": "تاریخ پایان هفته به فرمت YYYY-MM-DD",
      "description": "توضیح عملکرد هفتگی",
      "transaction_count": عدد صحیح,
      "net_profit": عدد اعشاری,
      "win_rate": عدد اعشاری بین ۰ تا ۱۰۰,
      "adherence_to_the_plan": عدد اعشاری بین ۰ تا ۱۰۰,
      "best_trade": "نام نماد بهترین معامله",
      "worst_trade": "نام نماد بدترین معامله",
      "golden_window": "بازه‌ی زمانی طلایی معاملات آن هفته"
    }}
  ],
  "suggested_exercises": [
    {{ "text": "متن تمرین پیشنهادی" }}
  ]
}}
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


@extend_schema(tags=["AI Analysis"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_analysis_view(request):
    portfolio = Portfolio.objects.filter(user=request.user, is_active=True).first()
    if not portfolio:
        return Response({"error": "پورتفوی فعالی یافت نشد."}, status=404)

    analysis = AIAnalysis.objects.filter(portfolio=portfolio).order_by('-date').first()

    if analysis:
        serializer = AIAnalysisSerializer(analysis)
        return Response(serializer.data, status=200)

    try:
        default_model = AIModel.objects.filter(is_default=True).first()
        if not default_model:
            return Response({"error": "مدل پیش‌فرض هوش مصنوعی یافت نشد."}, status=400)

        analysis = generate_and_save_ai_analysis(portfolio, ai_model=default_model)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    serializer = AIAnalysisSerializer(analysis)
    return Response(serializer.data, status=201)