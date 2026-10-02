import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
	api_view,
	authentication_classes,
	permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app_user.models import UserSubscription
from .models import Payment
from .serializers import (
	PaymentRequestResponseSerializer,
	PaymentRequestSerializer,
	PaymentVerifyResponseSerializer,
)


logger = logging.getLogger(__name__)
GATEWAY_TIMEOUT_SECONDS = 10


@extend_schema(
	tags=['Payment'],
	request=PaymentRequestSerializer,
	responses={201: PaymentRequestResponseSerializer},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
	serializer = PaymentRequestSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	subscription = serializer.validated_data['subscription_id']
	amount = subscription.price * 10

	metadata = {'email': request.user.email} if request.user.email else {}
	if request.user.phone:
		metadata['mobile'] = request.user.phone

	try:
		gateway_response = requests.post(
			settings.ZARINPAL_URL_REQUEST,
			json={
				'merchant_id': settings.ZARINPAL_MERCHANT,
				'amount': amount,
				'callback_url': settings.ZARINPAL_CALLBACK_URL,
				'description': f'Subscription payment: {subscription.name}',
				'metadata': metadata,
			},
			timeout=GATEWAY_TIMEOUT_SECONDS,
		)
		gateway_response.raise_for_status()
		gateway_data = gateway_response.json().get('data', {})
	except (requests.RequestException, ValueError, AttributeError):
		logger.exception('Zarinpal payment request failed')
		return Response(
			{'success': False, 'code': 'GATEWAY_REQUEST_FAILED'},
			status=502,
		)

	authority = gateway_data.get('authority')
	if gateway_data.get('code') != 100 or not authority:
		return Response(
			{'success': False, 'code': 'GATEWAY_REJECTED_REQUEST'},
			status=502,
		)

	Payment.objects.create(
		authority=authority,
		amount=amount,
		subscription=subscription,
		user=request.user,
	)
	return Response(
		{
			'success': True,
			'authority': authority,
			'payment_url': f'{settings.ZARINPAL_URL_START_PAY}{authority}',
		},
		status=201,
	)


@extend_schema(
	tags=['Payment'],
	responses={200: PaymentVerifyResponseSerializer},
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_payment(request):
	authority = request.query_params.get('Authority')
	if not authority:
		return Response(
			{'success': False, 'code': 'MISSING_AUTHORITY'},
			status=400,
		)

	payment = get_object_or_404(
		Payment.objects.select_related('subscription', 'user'),
		authority=authority,
	)
	if payment.is_paid:
		return Response({
			'success': True,
			'code': 'ALREADY_VERIFIED',
			'message': 'Payment was already verified.',
			'ref_id': payment.ref_id,
		})

	if request.query_params.get('Status') != 'OK':
		return Response(
			{
				'success': False,
				'code': 'PAYMENT_NOT_COMPLETED',
				'message': 'The payment was not completed.',
			},
			status=400,
		)

	try:
		gateway_response = requests.post(
			settings.ZARINPAL_URL_VERIFY,
			json={
				'merchant_id': settings.ZARINPAL_MERCHANT,
				'amount': payment.amount,
				'authority': payment.authority,
			},
			timeout=GATEWAY_TIMEOUT_SECONDS,
		)
		if not gateway_response.ok:
			logger.error(
				'Zarinpal payment request HTTP %s response: %s',
				gateway_response.status_code,
				gateway_response.text[:2000],
			)
			
		gateway_response.raise_for_status()
		gateway_data = gateway_response.json().get('data', {})
	except (requests.RequestException, ValueError, AttributeError):
		logger.exception('Zarinpal payment verification failed')
		return Response(
			{'success': False, 'code': 'GATEWAY_VERIFY_FAILED'},
			status=502,
		)

	if gateway_data.get('code') not in (100, 101):
		return Response(
			{
				'success': False,
				'code': 'PAYMENT_NOT_VERIFIED',
				'message': 'Zarinpal did not verify the payment.',
			},
			status=400,
		)

	today = timezone.localdate()
	with transaction.atomic():
		payment = Payment.objects.select_for_update().get(pk=payment.pk)
		if payment.is_paid:
			return Response({
				'success': True,
				'code': 'ALREADY_VERIFIED',
				'message': 'Payment was already verified.',
				'ref_id': payment.ref_id,
			})

		user_subscription = (
			UserSubscription.objects.select_for_update()
			.filter(user=payment.user)
			.first()
		)
		if user_subscription is None:
			user_subscription = UserSubscription.objects.create(
				user=payment.user,
				type=payment.subscription,
				start_date=today,
				end_date=today + timedelta(days=30),
			)
		else:
			if user_subscription.end_date and user_subscription.end_date >= today:
				user_subscription.end_date += timedelta(days=30)
			else:
				user_subscription.start_date = today
				user_subscription.end_date = today + timedelta(days=30)
			user_subscription.type = payment.subscription
			user_subscription.save(
				update_fields=['type', 'start_date', 'end_date'],
			)

		payment.is_paid = True
		payment.ref_id = gateway_data.get('ref_id')
		payment.save(update_fields=['is_paid', 'ref_id'])

	return Response({
		'success': True,
		'code': 'PAYMENT_VERIFIED',
		'message': 'Payment verified and subscription updated.',
		'ref_id': payment.ref_id,
	})
