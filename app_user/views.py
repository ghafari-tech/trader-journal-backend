import secrets
from datetime import timedelta
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from app_admin.views import subscriptions_list
from app_setting.models import Subscription
from app_user.models import User, EmailVerificationCode, UserSubscription
from .serializers import *


@extend_schema(request=RegisterSerializer, tags=["Authentication"])
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    first_name = serializer.validated_data["first_name"]
    last_name = serializer.validated_data["last_name"]
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = User.objects.filter(email=email).first()

    if user:
        if user.is_verified:
            return Response({
                "message": "This account already exists. Please login."
            }, status=400)
        else:
            code = str(secrets.randbelow(1_000_000)).zfill(6)

            EmailVerificationCode.objects.create(
                user=user,
                code=code,
                expires_at=timezone.now() + timedelta(minutes=5)
            )

            send_mail(
                subject="کد تایید ایمیل",
                message=f"""
                به اپلیکیشن تریدر جورنال خوش آمدید
                کد تایید:

                {code}

                این کد محرمانه هست و نباید به کسی بدهید
                هرکس این کد را بخواهد قطعا کلاهبردار است

                این کد تا ۵ دقیقه در دسترس شما خواهد بود
                """,
                from_email=None,
                recipient_list=[user.email],
            )

            return Response({
                "message": "Verification code sent successfully.",
                "email": email,
            }, status=201)


    with transaction.atomic():
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        subscription = Subscription.objects.get(name='Free')

        UserSubscription.objects.create(
            user=user,
            type=subscription,
        )

        code = str(secrets.randbelow(1_000_000)).zfill(6)

        EmailVerificationCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        send_mail(
            subject="Email Verification Code",
            message=f"""
            به اپلیکیشن تریدر جورنال خوش آمدید
            کد تایید:

            {code}

            این کد محرمانه هست و نباید به کسی بدهید
            هرکس این کد را بخواهد قطعا کلاهبردار است

            این کد تا ۵ دقیقه در دسترس شما خواهد بود
            """,
            from_email=None,
            recipient_list=[user.email],
        )

    return Response({
        "message": "Verification code sent successfully.",
        "email": email,
    }, status=201)



@extend_schema(request=VerifyEmailSerializer, tags=["Authentication"])
@api_view(["POST"])
def verify_register(request):
    serializer = VerifyEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"]

    try:
        user = User.objects.get(email=email, is_verified=False)
    except User.DoesNotExist:
        return Response({
            "message": "This account does not exist.",
        }, status=400)

    verification = EmailVerificationCode.objects.filter(
        user=user,
        code=code,
        is_used=False,
    ).order_by("-created_at").first()

    if verification is None or not verification.is_valid():
        return Response({
            "message": "Invalid or expired verification code.",
        }, status=400)

    verification.is_used = True
    verification.save(update_fields=["is_used"])

    user.is_verified = True
    user.save(update_fields=["is_verified"])

    return Response({
        "message": "Account has been verified successfully. Please login.",
    }, status=200)


@extend_schema(request=LoginSerializer, tags=['Authentication'])
@api_view(['POST'])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(
        request,
        email=email,
        password=password
    )

    if user is None:
        return Response({
            "message": "Invalid email or password",
        }, status=401)

    if not user.is_verified:
        return Response({
            "message": "Please verify your email before login.",
        }, status=403)

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login Successful",
        "user_id": user.id,
        "email": user.email,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })

@extend_schema(request=LogoutSerializer, tags=['Authentication'])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response({
            "message": "Refresh token is required."
        }, status=400)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            "message": "Logout successful"
        }, status=200)

    except Exception:
        return Response({
            "message": "Invalid refresh token."
        }, status=400)
    

@extend_schema(tags=['Authentication'], request=ForgotPasswordSerializer)
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email', None)

    try:
        if not email:
            return Response({
                "message": "Email is required."
            }, status=400)

        user = User.objects.get(email=email)
        if not user:
            return Response({
                "message": "User with this email does not exist."
            }, status=404)
        if not user.is_verified:
            return Response({
                "message": "Please verify your email before resetting password(register first).",
            }, status=403)

        code = str(secrets.randbelow(1_000_000)).zfill(6)

        EmailVerificationCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        send_mail(
            subject="Password Reset Code",
            message=f"""
            تریدر جورنال - کد بازیابی رمز عبور:

            {code}

            این کد محرمانه هست و نباید به کسی بدهید
            هرکس این کد را بخواهد قطعا کلاهبردار است
            این کد تا ۵ دقیقه در دسترس شما خواهد بود
            """,
            from_email=None,
            recipient_list=[user.email],
        )

        return Response({
            "message": "Password reset code sent successfully.",
            "email": email,
        }, status=200)
    except User.DoesNotExist:
        return Response({
            "message": "User with this email does not exist."
        }, status=404)
    
    except Exception as e:
        return Response({
            "message": "An error occurred while processing your request.",
            "error": str(e)
        }, status=500)

@extend_schema(request=ResetPasswordSerializer, tags=['Authentication'])
@api_view(['POST'])
def reset_password(request):
    """حتما دوبار پسورد جدید رو باید وارد کنید و چک کنید که با هم برابر باشند"""
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    code = serializer.validated_data['code']
    new_password = serializer.validated_data['new_password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "message": "User with this email does not exist."
        }, status=404)

    verification = EmailVerificationCode.objects.filter(
        user=user,
        code=code,
        is_used=False,
    ).order_by("-created_at").first()

    if verification is None or not verification.is_valid():
        return Response({
            "message": "Invalid or expired verification code.",
        }, status=400)

    user.set_password(new_password)
    user.save()

    verification.is_used = True
    verification.save(update_fields=["is_used"])

    return Response({
        "message": "Password has been reset successfully. Please login with your new password.",
    }, status=200)


