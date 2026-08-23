from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *

@extend_schema(tags=['Risk Management'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def risk_management_show(request):
    risk_manage, created = RiskManagement.objects.get_or_create(
        user=request.user,
    )

    serializer = RiskManageSerializer(risk_manage)

    return Response({
        'riskmanage': serializer.data,
    }, status=200)

@extend_schema(tags=['Risk Management'], request=EditRiskManageSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_risk_management(request):
    max_risk = request.data.get('max_risk')
    max_loss_daily = request.data.get('max_loss_daily')
    max_loss_weekly = request.data.get('max_loss_weekly')
    max_transaction_daily = request.data.get('max_transaction_daily')
    max_consecutive_loss = request.data.get('max_consecutive_loss')

    risk_manage, created = RiskManagement.objects.get_or_create(
        user=request.user,
    )

    if max_risk != risk_manage.max_risk:
        risk_manage.max_risk = max_risk
    if max_loss_daily != risk_manage.max_loss_daily:
        risk_manage.max_loss_daily = max_loss_daily
    if max_loss_weekly != risk_manage.max_loss_weekly:
        risk_manage.max_loss_weekly = max_loss_weekly
    if max_transaction_daily != risk_manage.max_transaction_daily:
        risk_manage.max_transaction_daily = max_transaction_daily
    if max_consecutive_loss != risk_manage.max_consecutive_loss:
        risk_manage.max_consecutive_loss = max_consecutive_loss

    risk_manage.save()

    return Response({
        'message': 'Risk Management has been updated.',
    }, status=200)


