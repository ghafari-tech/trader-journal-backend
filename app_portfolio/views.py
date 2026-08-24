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
    portfolios = Portfolio.objects.filter(user=request.user, is_archived=False)

    serializer = PortfolioSerializer(portfolios, many=True)

    return Response({
        'portfolios': serializer.data
    }, status=200)

@extend_schema(
    tags=['Portfolio'],
    request=AddPortfolioSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def portfolio_create(request):
    serializer = AddPortfolioSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=400)

    portfolio = serializer.save(user=request.user)

    return Response({
        'message': 'Portfolio created successfully',
        'portfolio': AddPortfolioSerializer(portfolio).data
    }, status=201)

@extend_schema(
    tags=['Portfolio'],
    request=AddPortfolioSerializer
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def portfolio_edit(request, pk):
    portfolio = get_object_or_404(
        Portfolio,
        pk=pk,
        user=request.user
    )

    serializer = AddPortfolioSerializer(
        portfolio,
        data=request.data
    )

    if not serializer.is_valid():
        return Response({
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=400)

    portfolio = serializer.save()

    return Response({
        'message': 'Portfolio updated successfully',
        'portfolio': AddPortfolioSerializer(portfolio).data
    }, status=200)


@extend_schema(tags=['Portfolio'])
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def portfolio_delete(request, pk):
    portfolio = get_object_or_404(
        Portfolio,
        pk=pk,
        user=request.user
    )

    portfolio.delete()

    return Response({
        'message': 'Portfolio deleted successfully'
    }, status=200)

@extend_schema(tags=['Portfolio'])
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def portfolio_archive(request, pk):
    portfolio = get_object_or_404(
        Portfolio,
        pk=pk,
        user=request.user
    )

    portfolio.is_archived = True
    portfolio.save(update_fields=['is_archived'])

    return Response({
        'message': 'Portfolio archived successfully'
    }, status=200)