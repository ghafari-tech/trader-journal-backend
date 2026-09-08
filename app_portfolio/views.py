from cffi.model import pointer_cache

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

@extend_schema(tags=['Portfolio'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_archive_list(request):
    portfolios = Portfolio.objects.filter(user=request.user, is_archived=True)
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

    if not Portfolio.objects.filter(user=request.user, is_active=True).exists():
        portfolio.is_active = True

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

    if portfolio.is_active:
        porto = Portfolio.objects.filter(user=request.user, is_archived=False).order_by('created_at').first()
        porto.is_active = True
        porto.save()

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

    if portfolio.is_active:
        porto = Portfolio.objects.filter(user=request.user, is_archived=True).order_by('created_at').first()
        porto.is_active = True
        porto.save()

    return Response({
        'message': 'Portfolio archived successfully'
    }, status=200)

@extend_schema(tags=['Portfolio'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_portfolio(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    portfolio.is_active = True
    portfolio.save()
    return Response({
        'message': 'Portfolio active successfully',
    }, status=201)

def archive_out_portfolio(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    if not portfolio:
        return Response({
            'message': 'Portfolio does not exist',
        }, status=404)

    if not portfolio.is_archived:
        return Response({
            'message': 'Portfolio not archive',
        }, status=403)

    portfolio.is_archived = False
    portfolio.save()

    return Response({
        'message': 'Portfolio archived successfully',
    }, status=201)