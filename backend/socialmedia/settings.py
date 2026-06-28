"""
settings.py — Django Project Configuration
============================================
Key sections:
  1. Core Django settings (SECRET_KEY, INSTALLED_APPS, etc.)
  2. Database — SQLite by default (swap to PostgreSQL for production)
  3. Django REST Framework — authentication + permissions
  4. Simple JWT — token lifetimes
  5. CORS — allow the frontend (HTML/JS) to call the API
  6. Media files — avatars & post images
"""

from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────
SECRET_KEY = 'django-insecure-replace-this-in-production-with-a-random-50-char-string'
DEBUG = True
ALLOWED_HOSTS = ['*']   # restrict to your domain in production

# ── Apps ──────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',               # Django REST Framework
    'rest_framework_simplejwt',     # JWT authentication
    'corsheaders',                  # Allow cross-origin requests from frontend

    # Our app
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # must be FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'socialmedia.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR.parent / 'frontend'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'socialmedia.wsgi.application'

# ── Database ───────────────────────────────────────────────
# SQLite is fine for development.
# For production, use PostgreSQL:
#   DATABASES = {
#     'default': {
#       'ENGINE': 'django.db.backends.postgresql',
#       'NAME': 'socialmedia_db',
#       'USER': 'postgres',
#       'PASSWORD': 'yourpassword',
#       'HOST': 'localhost',
#       'PORT': '5432',
#     }
#   }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Custom User Model ──────────────────────────────────────
# Must be set BEFORE the first migration.
AUTH_USER_MODEL = 'core.User'

# ── Django REST Framework ──────────────────────────────────
REST_FRAMEWORK = {
    # Use JWT Bearer tokens for authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # By default, unauthenticated users can only read (GET)
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    # Return JSON by default (no browsable API HTML in production)
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# ── JWT Token Settings ─────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),    # short-lived access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # longer-lived refresh token
    'ROTATE_REFRESH_TOKENS': True,                  # new refresh token on each refresh
    'AUTH_HEADER_TYPES': ('Bearer',),               # Authorization: Bearer <token>
}

# ── CORS ───────────────────────────────────────────────────
# Allow the HTML frontend (opened as file:// or localhost) to call the API.
CORS_ALLOW_ALL_ORIGINS = True   # In production: list specific origins instead
# CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']

# ── Media Files ────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Static Files ───────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Misc ───────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True