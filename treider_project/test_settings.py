"""Settings used only for running the test suite.

It reuses the real project settings but swaps PostgreSQL for an in-memory
SQLite database, disables real email sending and uses a fast password hasher.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

DEBUG = False

# Keep tests hermetic: never hit the real Zarinpal gateway unless patched.
ZARINPAL_MERCHANT = "00000000-0000-0000-0000-000000000000"
