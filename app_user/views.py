from django.contrib.auth import authenticate
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from app_user.models import User, EmailVerificationCode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import *


def user_view(request):
    user = request.user
    return JsonResponse({
        "image_profile": user.image_profile,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone
    })

def change_profile(request):
    pass

@extend_schema(request=RegisterSerializer, tags=['Authentication'])
@api_view(['POST'])
def register(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get("email")
    password = request.data.get("password")

    user = User.objects.filter(email=email).first()
    if user:
        return Response({
            "message": "This account already exists. Please login."
        }, status=400)


    user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )

    return Response({
        "message": "User created successfully.",
        "email": email
    }, status=200)

    # code = str(secrets.randbelow(1_000_000)).zfill(6)
    #
    # verification = EmailVerificationCode.objects.create(
    #     user=user,
    #     code=code,
    #     expires_at=timezone.now() + timedelta(minutes=5)
    # )
    #
    # send_mail(
    #     subject="Email Verification Code",
    #     message=f"""
    # Your verification code is:
    #
    # {code}
    #
    # This code is confidential.
    # Never share this code with anyone.
    #
    # If someone asks you for this code, they are trying to scam you.
    #
    # This code expires in 5 minutes.
    # """,
    #     from_email=None,
    #     recipient_list=[user.email],
    # )
    #
    # return Response({
    #     "message": "sent code.",
    # }, status=201)



# @extend_schema(request=VerifyEmailSerializer, tags=['Authentication'])
# @api_view(['POST'])
# def verify(request):
#     email = request.data.get("email")
#     code = request.data.get("code")
#
#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response({
#             "message": "This account does not exist.",
#         }, status=400)
#
#     verification = EmailVerificationCode.objects.filter(
#         user=user,
#         code=code,
#         is_used=False
#     ).order_by(
#         "-created_at"
#     ).first()
#
#     if verification is None or not verification.is_valid():
#         return Response({
#             "message": "Invalid or expired verification code.",
#         }, status=400)
#
#     verification.is_used = True
#     verification.save(update_fields=["is_used"])
#
#     user.is_active = True
#     user.save(update_fields=["is_active"])
#
#     return Response({
#         "message": "Account has been verified, register successfully. please login.",
#     }, status=200)


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

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login Successful",
        "user_id": user.id,
        "email": user.email,
        "access": str(refresh.access_token),
        "refresh": str(refresh)
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
