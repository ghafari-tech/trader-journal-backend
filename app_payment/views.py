import requests
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentRequestSerializer
from app_setting.models import Subscription
from app_user.models import UserSubscription

class PaymentRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        if serializer.is_valid():
            subscription_id = serializer.validated_data['subscription_id']
            try:
                subscription = Subscription.objects.get(id=subscription_id)
            except Subscription.DoesNotExist:
                return Response({"error": "Subscription plan not found"}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT,
                "amount": subscription.price,
                "description": f"Purchase {subscription.name} for {request.user.email}",
                "callback_url": settings.ZARINPAL_CALLBACK_URL,
            }
            
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            try:
                response = requests.post(settings.ZARINPAL_URL_REQUEST, json=data, headers=headers)
                res_data = response.json()
                
                # In Zarinpal v4, data is inside 'data' key
                if 'data' in res_data and res_data['data'] and res_data['data']['code'] == 100:
                    authority = res_data['data']['authority']
                    Payment.objects.create(
                        user=request.user,
                        subscription=subscription,
                        authority=authority,
                        amount=subscription.price
                    )
                    return Response({
                        "payment_url": f"{settings.ZARINPAL_URL_START_PAY}{authority}"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Error from Zarinpal", "details": res_data}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerifyView(views.APIView):
    def get(self, request):
        authority = request.query_params.get('Authority')
        status_pay = request.query_params.get('Status')

        if status_pay == 'OK':
            try:
                payment = Payment.objects.get(authority=authority, is_paid=False)
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found or already processed"}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT,
                "amount": payment.amount,
                "authority": authority,
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            try:
                response = requests.post(settings.ZARINPAL_URL_VERIFY, json=data, headers=headers)
                res_data = response.json()

                if 'data' in res_data and res_data['data'] and res_data['data']['code'] in [100, 101]:
                    payment.is_paid = True
                    payment.ref_id = res_data['data']['ref_id']
                    payment.save()

                    # Update user plan
                    user_sub, created = UserSubscription.objects.get_or_create(user=payment.user, defaults={'type': payment.subscription})
                    if not created:
                        user_sub.type = payment.subscription
                    
                    user_sub.start_date = timezone.now().date()
                    # Example: plan for 30 days
                    user_sub.end_date = (timezone.now() + timezone.timedelta(days=30)).date()
                    user_sub.save()

                    return Response({
                        "message": "Payment successful",
                        "ref_id": payment.ref_id,
                        "plan": payment.subscription.name
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Payment failed or verification failed", "details": res_data}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"error": "Payment cancelled by user or failed"}, status=status.HTTP_400_BAD_REQUEST)

