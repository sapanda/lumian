"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from enum import Enum
from google.oauth2 import service_account
import os
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'changeme')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

ALLOWED_HOSTS = []
ALLOWED_HOSTS.extend(
    filter(
        None,
        os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(','),
    )
)

CSRF_TRUSTED_ORIGINS = []
CSRF_TRUSTED_ORIGINS.extend(
    filter(
        None,
        os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(','),
    )
)

if os.environ.get('DJANGO_ALLOWED_ORIGINS'):
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOWED_ORIGINS.extend(
        filter(
            None,
            os.environ.get('DJANGO_ALLOWED_ORIGINS', '').split(',')
        )
    )
else:
    CORS_ALLOW_ALL_ORIGINS = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "meeting": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "transcript": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "project": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'core',
    'user',
    'project',
    'transcript',
    'meeting'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Deployment parameters
class ModeEnum(str, Enum):
    local = 'local'
    github = 'github'
    development = 'dev'
    production = 'prod'


DEPLOY_MODE = ModeEnum(os.environ.get('DEPLOY_MODE', ModeEnum.local))
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'app.renderers.ApiRenderer',
    ),
}

SPECTACULAR_SETTINGS = {
    'COMPONENT_SPLIT_REQUEST': True
}

# Synthesis settings
SYNTHESIS_URL = os.environ.get('SYNTHESIS_URL')
SYNTHESIS_TASK_TIMEOUT = int(os.environ.get('SYNTHESIS_TASK_TIMEOUT', 10))

# Recall AI settings
RECALL_API_KEY = os.environ.get("RECALL_API_KEY")
RECALL_TRANSCRIPT_PROVIDER = os.environ.get("RECALL_TRANSCRIPT_PROVIDER")
ASSEMBLY_API_KEY = os.environ.get("ASSEMBLY_API_KEY")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL")

MICROSOFT_CLIENT_ID = os.environ.get("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.environ.get("MICROSOFT_CLIENT_SECRET")
MICROSOFT_REDIRECT_URL = os.environ.get("MICROSOFT_REDIRECT_URL")
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/static/'
MEDIA_URL = '/static/media/'

STATIC_ROOT = '/vol/web/static'
MEDIA_ROOT = '/vol/web/media'

if DEPLOY_MODE == ModeEnum.development or DEPLOY_MODE == ModeEnum.production:
    GCLOUD_PROJECT_ID = os.environ.get('GCLOUD_PROJECT_ID')
    GCLOUD_LOCATION = os.environ.get('GCLOUD_LOCATION')
    GCLOUD_QUEUE_NAME = os.environ.get('GCLOUD_QUEUE_NAME')
    GCLOUD_API_SERVICE_NAME = os.environ.get('GCLOUD_API_SERVICE_NAME')
    GCLOUD_API_SERVICE_URL = os.environ.get('GCLOUD_API_SERVICE_URL')

    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GCLOUD_BUCKET_NAME')
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.environ.get('GCLOUD_SECRETS_PATH')
    )

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        environment=DEPLOY_MODE.value,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )
else:
    GCLOUD_EMULATOR_URL = os.environ.get('GCLOUD_EMULATOR_URL')
    GCLOUD_EMULATOR_SERVICE_URL = os.environ.get('GCLOUD_EMULATOR_SERVICE_URL')
