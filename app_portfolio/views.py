from .serializers import *
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


@extend_schema(tags=['Portfolio'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)

    serializer = PortfolioSerializer(portfolios, many=True)

    return Response({
        'portfolios': serializer.data
    }, status=200)
