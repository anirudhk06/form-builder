import uuid
import pytz
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

from db.mixins import TimeAuditModel

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    # choices
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        USER = "USER", "User"

    USER_TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255, default="")
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    avatar = models.TextField(blank=True)
    cover_image = models.URLField(blank=True, null=True, max_length=800)
    
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_location = models.CharField(max_length=255, blank=True)
    created_location = models.CharField(max_length=255, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_password_expired = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    token = models.CharField(max_length=64, blank=True)

    last_active = models.DateTimeField(default=timezone.now, null=True)
    last_login_time = models.DateTimeField(null=True)
    last_logout_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(max_length=20, default="email")
    last_login_uagent = models.TextField(blank=True)
    token_updated_at = models.DateTimeField(null=True)

    is_bot = models.BooleanField(default=False)
    role = models.CharField(max_length=100, choices=Role.choices)

    user_timezone = models.CharField(
        max_length=255, default="UTC", choices=USER_TIMEZONE_CHOICES
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.username} <{self.email}>"

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()


class Profile(TimeAuditModel):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )
    # User
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        db_table = "profiles"
        ordering = ("-created_at",)