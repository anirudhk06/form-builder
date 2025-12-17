import os
import dj_database_url
from .base import *

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

if bool(os.environ.get("DATABASE_URL")):
    DATABASES = {"default": dj_database_url.config()}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password reset time the number of seconds the uniquely generated uid will be valid
PASSWORD_RESET_TIMEOUT = 3600

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("ACCESS_TOKEN_LIFETIME", default=5)),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=env.int("REFRESH_TOKEN_LIFETIME", default=1440)),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": False,
}