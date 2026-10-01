from django.db import transaction
from drf_spectacular.utils import extend_schema
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



def generate_and_save_ai_analysis(portfolio, model_name=None):
    if model_name:
        ai_model = AIModel.objects.filter(name=model_name).first()
    else:
        ai_model = AIModel.objects.first()

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

    ai_response = {
        "weekly_report": "علی عزیز — هفته خوبی داشتی. پایبندی به حد ضرر تو ۹۲٪ بوده که عالی است...",
        "trading_regime": 78,
        "capital_management": 84,
        "psychology": 62,
        "adherence_to_the_plan": 71,
        "strengths": [
            {
                "title": "پایبندی بالا به حد ضرر در ۹۲٪ معاملات",
                "maintaining_sustainability": "قبل از هر معامله، SL را همان لحظه ورود در پلتفرم ثبت کن."
            }
        ],
        "weaknesses": [
            {
                "title": "الگوی Revenge Trading بعد از ۳ ضرر متوالی",
                "solution": "بعد از ۲ ضرر متوالی، پلتفرم را قفل کن و ۳۰ دقیقه پیاده‌روی کن."
            }
        ],
        "performance_days": [
            {
                "date": "2024-10-23", 
                "description": "گزارش عملکرد روزانه...",
                "transaction_count": 4,
                "net_profit": 588.00,
                "win_rate": 75.0,
                "adherence_to_the_plan": 75.0,
                "best_trade": "EURUSD",
                "worst_trade": "US30",
                "golden_window": "۱۰:۰۰ تا ۱۳:۰۰"
            }
        ],
        "suggested_exercises": [
            {"text": "۳ روز فقط ست‌آپ‌های +A ترید کن."},
            {"text": "قبل از هر معامله، دلیل ورود را بنویس."}
        ]
    }

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
                title=strength['title'],
                maintaining_sustainability=strength['maintaining_sustainability']
            )

        for weakness in ai_response.get("weaknesses", []):
            Weaknesses.objects.create(
                analysis=analysis,
                title=weakness['title'],
                solution=weakness['solution']
            )

        for day_report in ai_response.get("performance_days", []):
            PerformanceReportDay.objects.create(
                analysis=analysis,
                date=day_report['date'],
                description=day_report['description'],
                transaction_count=day_report['transaction_count'],
                net_profit=day_report['net_profit'],
                win_rate=day_report['win_rate'],
                adherence_to_the_plan=day_report['adherence_to_the_plan'],
                best_trade=day_report['best_trade'],
                worst_trade=day_report['worst_trade'],
                golden_window=day_report['golden_window']
            )

        for exercise in ai_response.get("suggested_exercises", []):
            SuggestedExercises.objects.create(
                analysis=analysis,
                text=exercise['text']
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
        model_name = default_model.name if default_model else None
        
        analysis = generate_and_save_ai_analysis(portfolio, model_name=model_name)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    serializer = AIAnalysisSerializer(analysis)
    return Response(serializer.data, status=201)