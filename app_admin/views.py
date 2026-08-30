from treider_project import settings
from .serializers import *
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app_user.models import User, Subscription


@extend_schema(tags=['Admin'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    if request.user.email != settings.ADMIN_EMAIL:
        return Response({
            'message': 'you are not allowed to access this endpoint',
        }, status=403)
    users = User.objects.all()

    for user in users:
        if not hasattr(user, "plan"):
            Subscription.objects.create(user=user)

    serializer = UserAdminSerializer(users, many=True)

    return Response({
        'users': serializer.data
    }, status=200)
