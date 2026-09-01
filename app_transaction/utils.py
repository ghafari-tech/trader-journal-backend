from cryptography.fernet import Fernet
from django.conf import settings

_fernet = Fernet(settings.MT_INVESTOR_PASSWORD_KEY.encode())

def encrypt_password(raw: str) -> str:
    return _fernet.encrypt(raw.encode()).decode()

def decrypt_password(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()