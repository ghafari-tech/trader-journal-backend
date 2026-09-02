from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import MetaTraderAccount


class MetaTraderApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None
        try:
            account = MetaTraderAccount.objects.get(api_key=api_key)
        except MetaTraderAccount.DoesNotExist:
            raise AuthenticationFailed('کلید API نامعتبر است')
        return (account.user, account)