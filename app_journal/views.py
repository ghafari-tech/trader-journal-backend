from django.contrib.auth import authenticate
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema

from app_transaction.models import Transaction
from app_user.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Journal
from .serializers import *

@extend_schema(tags=['Journal'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_list(request):
    journals = Journal.objects.filter(user=request.user)

    serializer = JournalSerializer(journals, many=True)

    return Response({
        'journals': serializer.data
    }, status=200)

@extend_schema(tags=['Journal'], request=AddJournalSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_journal(request):
    title = request.data.get('title')
    transaction_id = request.data.get('transaction_id')
    feel = request.data.get('feel')
    mistakes = request.data.get('mistakes')
    lesson_learned = request.data.get('lesson_learned')
    followed_plan = request.data.get('followed_plan')

    valid_feels = [
        "comfort",
        "concentrated",
        "greed",
        "fear",
        "revenge"
    ]

    if not title or not feel or not mistakes or not lesson_learned or not followed_plan:
        return JsonResponse({
            'success': False,
            'message': 'Please fill in all the required fields.'
        }, status=400)

    if not transaction_id.startswith('T-'):
        if transaction_id != "" or transaction_id:
            return JsonResponse({
                'success': False,
                'message': 'Transaction ID must start with T-.'
            }, status=400)

    if feel not in valid_feels:
        return JsonResponse({
            'success': False,
            'message': 'Feel free to choose one of the following.'
        }, status=400)

    if transaction_id:
        transaction = Transaction.objects.filter(transaction_id=transaction_id, portfolio__user=request.user).first()
        if not transaction:
            return JsonResponse({
                'success': False,
                'message': 'Transaction does not exist.'
            }, status=400)
    else:
        transaction = None


    journal = Journal.objects.create(
        user=request.user,
        transaction = transaction if transaction_id else None,
        title=title,
        feel=feel,
        mistakes=mistakes,
        lesson_learned=lesson_learned,
        followed_plan=followed_plan,
    )
    return JsonResponse({
        'success': True,
        'journal_id': journal.id,
        'message': 'Journal created'
    }, status=200)
