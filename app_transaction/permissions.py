from rest_framework.permissions import BasePermission
from django.conf import settings


class HasInternalSecret(BasePermission):
    """
    فقط برای ارتباط سرور-به-سرور (بین دو نمونه از همین پروژه).
    هیچ کاربر واقعی این پرمیشن رو نمی‌گیره.
    """
    def has_permission(self, request, view):
        secret = request.headers.get('X-Internal-Secret')
        return bool(secret) and secret == settings.MT5_INTERNAL_SECRET