from drf_spectacular.utils import extend_schema
from app_user.models import Subscription
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *


@extend_schema(tags=['User Info'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_plan_info(request):
    plan = Subscription.objects.filter(user=request.user).first()

    if not plan:
        plan = Subscription.objects.create(user=request.user)

    serializer = UserPlanSerializer(plan)

    return Response({
        'plan': serializer.data,
    })