"""
Django settings for the StickForStats project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-development-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    # 'pgvector.django',  # Temporarily disabled due to installation issues
    
    # StickForStats apps - Core
    'stickforstats.core.apps.CoreConfig',
    
    # StickForStats modules
    'stickforstats.confidence_intervals.apps.ConfidenceIntervalsConfig',
    # Additional modules to enable as we migrate them
    # 'stickforstats.probability_distributions.apps.ProbabilityDistributionsConfig',
    # 'stickforstats.sqc_analysis.apps.SQCAnalysisConfig',
    # 'stickforstats.doe_analysis.apps.DOEAnalysisConfig',
    # 'stickforstats.pca_analysis.apps.PCAAnalysisConfig',
    # 'stickforstats.rag_system.apps.RagSystemConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stickforstats.mainapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'stickforstats.mainapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [BASE_DIR / 'stickforstats' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer' if DEBUG else 'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'stickforstats-cache',
    }
}

# RAG System settings (temporarily disabled)
# RAG_SYSTEM = {
#     'VECTOR_DB_PATH': os.environ.get('RAG_VECTOR_DB_PATH', BASE_DIR / 'vector_db'),
#     'DOCUMENTS_PATH': os.environ.get('RAG_DOCUMENTS_PATH', BASE_DIR / 'documents'),
#     'MODEL_NAME': os.environ.get('RAG_MODEL_NAME', 'all-MiniLM-L6-v2'),  # Default to a small model
#     'VECTOR_SIZE': int(os.environ.get('RAG_VECTOR_SIZE', 384)),  # Depends on the model
#     'CHUNK_SIZE': int(os.environ.get('RAG_CHUNK_SIZE', 300)),
#     'CHUNK_OVERLAP': int(os.environ.get('RAG_CHUNK_OVERLAP', 50)),
#     'RETRIEVAL_TOP_K': int(os.environ.get('RAG_RETRIEVAL_TOP_K', 5)),
#     'API_KEY': os.environ.get('RAG_API_KEY', ''),
#     'API_URL': os.environ.get('RAG_API_URL', ''),
#     'CACHE_EMBEDDINGS': os.environ.get('RAG_CACHE_EMBEDDINGS', 'True') == 'True',
#     'MAX_QUERY_LENGTH': int(os.environ.get('RAG_MAX_QUERY_LENGTH', 1000)),
#     'MAX_CONVERSATION_LENGTH': int(os.environ.get('RAG_MAX_CONVERSATION_LENGTH', 20)),
# }

# Data Service settings
DATA_SERVICE = {
    'CACHE_TIMEOUT': 3600,  # 1 hour
    'TEMP_DIR': 'temp',
    'ALLOW_CUSTOM_TRANSFORMATIONS': DEBUG,  # Only allow in development
}

# Module registry settings (temporarily disabled)
# MODULE_REGISTRY = {
#     'AUTODISCOVER_ENABLED': True,
#     'MODULES_PATH': 'stickforstats',
# }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'stickforstats.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'stickforstats': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Ensure logs directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Import local settings if they exist
try:
    from .local_settings import *
except ImportError:
    pass