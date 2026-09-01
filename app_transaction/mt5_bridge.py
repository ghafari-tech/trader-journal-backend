import threading

# چون MT5 در هر لحظه فقط یه اتصال فعال داره، درخواست‌های همزمان رو صف می‌کنیم
_mt5_lock = threading.Lock()


def connect_and_fetch_account(account_number, investor_password, server):
    """
    فقط روی ماشینی اجرا می‌شه که ترمینال MT5 و پکیج MetaTrader5 نصب باشه.
    """
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return {"success": False, "error": "پکیج MetaTrader5 روی این سرور نصب نیست"}

    with _mt5_lock:
        if not mt5.initialize():
            return {"success": False, "error": f"initialize failed: {mt5.last_error()}"}

        try:
            authorized = mt5.login(
                login=int(account_number),
                password=investor_password,
                server=server,
            )

            if not authorized:
                return {"success": False, "error": f"login failed: {mt5.last_error()}"}

            info = mt5.account_info()
            if info is None:
                return {"success": False, "error": "account_info برنگشت"}

            return {
                "success": True,
                "balance": info.balance,
                "equity": info.equity,
                "currency": info.currency,
                "name": info.name,
                "leverage": info.leverage,
                "server": info.server,
            }
        except Exception as e:
            return {"success": False, "error": f"خطای غیرمنتظره: {e}"}
        finally:
            mt5.shutdown()