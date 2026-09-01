import requests
from django.conf import settings


def call_mt5_verify_service(account_number, investor_password, server, timeout=15):
    try:
        response = requests.post(
            f"{settings.MT5_SERVICE_URL}/api/transaction/internal/mt5-verify/",
            json={
                "account_number": account_number,
                "investor_password": investor_password,
                "server": server,
            },
            headers={"X-Internal-Secret": settings.MT5_INTERNAL_SECRET},
            timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"سرویس متاتریدر در دسترس نیست: {e}"}

    try:
        return response.json()
    except ValueError:
        return {"success": False, "error": "پاسخ نامعتبر از سرویس"}