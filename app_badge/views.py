from .serializers import *
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404


@extend_schema(tags=['Badge'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def badge_list(request):
    badges = Badge.objects.all()

    serializer = BadgeSerializer(
        badges,
        many=True,
        context={'request': request}
    )

    return Response({
        'badges': serializer.data
    }, status=200)

@extend_schema(tags=['Badge'], request=AddBadgeSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_badge(request):
    name = request.data.get('name')
    description = request.data.get('description')

    if name and description:
        badge = Badge.objects.create(name=name, description=description)
        serializer = BadgeSerializer(badge)
        return Response(serializer.data, status=201)

    return Response({
        'message': 'please fill all fields'
    }, status=400)



# @extend_schema(tags=['Goal'], request=GoalInformationSerializer)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_goal(request):
#     title = request.data.get('title')
#     target_type = request.data.get('target_type')
#     target_value = request.data.get('target_value')
#     deadline = request.data.get('deadline')
#
#     portfolio = Portfolio.objects.filter(
#         user=request.user,
#         is_active=True
#     ).first()
#
#     valid_type = [
#         "profit",
#         "risk",
#         "order",
#         "learning"
#     ]
#
#     if title is None or target_type is None or target_value is None or deadline is None:
#         return Response({
#             'message': "please fill all fields"
#         }, status=400)
#
#
#     if target_type not in valid_type:
#         return Response({
#             'message': "type is not valid"
#         }, status=400)
#
#     goal = Goal.objects.create(
#         portfolio=portfolio,
#         title=title,
#         target_type=target_type,
#         target_value=target_value,
#         deadline=deadline,
#     )
#
#     return Response({
#         'message': 'goal created'
#     }, status=200)
#
#
# @extend_schema(tags=['Goal'], request=GoalInformationSerializer)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def edit_goal(request, pk):
#     goal = Goal.objects.get(pk=pk)
#     title = request.data.get('title')
#     target_type = request.data.get('target_type')
#     target_value = request.data.get('target_value')
#     deadline = request.data.get('deadline')
#
#     if title != goal.title:
#         goal.title = title
#     if target_type != goal.target_type:
#         goal.target_type = target_type
#     if target_value != goal.target_value:
#         goal.target_value = target_value
#     if deadline != goal.deadline:
#         goal.deadline = deadline
#
#     goal.save()
#     return Response({
#         'message': 'goal edited',
#         'goal_id': goal.id
#     }, status=200)
#
#
# @extend_schema(tags=['Goal'])
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_goal(request, pk):
#     goal = get_object_or_404(Goal, pk=pk)
#
#     if goal.user != request.user:
#         return Response({
#             'message': 'You do not have permission to delete this goal.'
#         }, status=403)
#
#     goal.delete()
#     return Response({
#         'message': 'goal deleted'
#     }, status=200)