"""
Configuration module for Django settings
Uses environment variables for sensitive information
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable or fallback to a default for development only
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-@_=r4ls@=cke_8&ljf79ua*s__gq_vnxzaonamck#0qdd*h%kc")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Database configuration
# Default to SQLite for development
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3")
DATABASE_NAME = os.environ.get("DATABASE_NAME", BASE_DIR / "db.sqlite3")
DATABASE_USER = os.environ.get("DATABASE_USER", "")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "")

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME = timedelta(
    minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 60))
)
JWT_REFRESH_TOKEN_LIFETIME = timedelta(
    days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7))
)

# Email configuration
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@globalitnet.com")

# API Keys
FORMATION_API_URL = os.environ.get("FORMATION_API_URL", "https://api.formations.example.com")
FORMATION_API_KEY = os.environ.get("FORMATION_API_KEY", "development-key-replace-in-production")

# File upload limits
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 5242880))  # 5MB default
ALLOWED_UPLOAD_EXTENSIONS = os.environ.get(
    "ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.pdf,.doc,.docx"
).split(",")

# CORS settings
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Static and media files
STATIC_URL = os.environ.get("STATIC_URL", "static/")
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, "staticfiles"))
MEDIA_URL = os.environ.get("MEDIA_URL", "media/")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))