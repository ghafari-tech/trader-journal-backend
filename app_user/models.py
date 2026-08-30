from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        if extra_fields.get("phone") == "":
            extra_fields["phone"] = None

        user = self.model(
            username=email,
            email=self.normalize_email(email),
            **extra_fields
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email,
            password,
            **extra_fields
        )

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(
            email,
            password,
            **extra_fields
        )

class User(AbstractUser):
    image_profile = models.ImageField()

    phone = models.CharField(
        max_length=11,
        unique=True,
	null=True,
	blank=True,
        validators=[
            RegexValidator(
                regex=r'09\d{9}$'
            )
        ]
    )

    status = models.CharField(
        max_length=8,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        default='active',
    )

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = UserManager()

    def __str__(self):
        return self.email



class EmailVerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes"
    )

    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (
            not self.is_used
            and timezone.now() < self.expires_at
        )

class Subscription(models.Model):
    SUBSCRIPTION_TYPE_CHOICES = [
        ('', 'Free'),
        ('pro', 'Pro'),
        ('pro max', 'ProMax')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="plan")
    type = models.CharField(
        max_length=7,
        choices=SUBSCRIPTION_TYPE_CHOICES,
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
