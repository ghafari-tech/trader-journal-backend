from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Badge, UserBadge
from .serializers import BadgeSerializer, AddBadgeSerializer, UserBadgeSerializer


@extend_schema(tags=['Badge'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def badge_list(request):
    badges = Badge.objects.all()
    serializer = BadgeSerializer(badges, many=True, context={'request': request})
    return Response({'badges': serializer.data}, status=200)


@extend_schema(tags=['Badge'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def badge_titles(request):
    titles = list(Badge.objects.values('id', 'name', 'description', 'icon'))
    return Response({'titles': titles}, status=200)


@extend_schema(tags=['Badge'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_badges(request):
    ubs = UserBadge.objects.filter(user=request.user).select_related('badge')
    serializer = UserBadgeSerializer(ubs, many=True)
    return Response({'badges': serializer.data}, status=200)


@extend_schema(tags=['Badge'], request=AddBadgeSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_badge(request):
    serializer = AddBadgeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    badge = serializer.save()
    return Response(
        BadgeSerializer(badge, context={'request': request}).data,
        status=201,
    )