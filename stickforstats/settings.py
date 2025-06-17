"""
Django settings for the StickForStats project.
"""

import os
from pathlib import Path

def read_secret(secret_name, default=None):
    """
    Read a secret from Docker secrets file or environment variable.
    Tries to read from /run/secrets/{secret_name} first, then falls back to environment variable.
    """
    secret_file = Path(f'/run/secrets/{secret_name}')
    if secret_file.exists():
        try:
            return secret_file.read_text().strip()
        except Exception:
            pass
    
    # Fall back to environment variable
    env_var = secret_name.upper().replace('-', '_')
    return os.environ.get(env_var, default)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = read_secret('django_secret_key', os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-development-only'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')

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
    'stickforstats.mainapp',
    'stickforstats.core.apps.CoreConfig',
    'stickforstats.rag_system.apps.RagSystemConfig',

    # StickForStats apps - Modules
    'stickforstats.confidence_intervals.apps.ConfidenceIntervalsConfig',
    'stickforstats.probability_distributions.apps.ProbabilityDistributionsConfig',
    'stickforstats.sqc_analysis.apps.SQCAnalysisConfig',
    'stickforstats.doe_analysis.apps.DOEAnalysisConfig',
    'stickforstats.pca_analysis.apps.PCAAnalysisConfig',
    'stickforstats.gpu_statistical_engine.apps.GpuStatisticalEngineConfig',
    
    # Enterprise modules
    'stickforstats.marketplace.apps.MarketplaceConfig',
    'stickforstats.collaboration.apps.CollaborationConfig',
    # 'stickforstats.machine_learning.apps.MachineLearningConfig',  # Temporarily disabled
    'stickforstats.advanced_statistics.apps.AdvancedStatisticsConfig',
    # 'stickforstats.automated_reporting.apps.AutomatedReportingConfig',  # Temporarily disabled
    'stickforstats.enterprise_security.apps.EnterpriseSecurityConfig',
    # 'stickforstats.data_visualization.apps.DataVisualizationConfig',  # Temporarily disabled
    
    # Workflow automation
    'stickforstats.workflow_automation.apps.WorkflowAutomationConfig',  # Re-enabled after fixing model conflict
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
    
    # Module-specific middleware
    'stickforstats.rag_system.middleware.RAGMetricsMiddleware',
    'stickforstats.rag_system.middleware.RAGSecurityMiddleware',
    'stickforstats.confidence_intervals.middleware.CIMetricsMiddleware',
]

ROOT_URLCONF = 'stickforstats.urls'

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

WSGI_APPLICATION = 'stickforstats.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': read_secret('db_password', os.environ.get('DATABASE_PASSWORD', '')),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', ''),
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

# Custom user model
AUTH_USER_MODEL = 'mainapp.User'

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
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = [
    'content-disposition',
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Cache settings
def get_redis_url(db_number=0):
    """Build Redis URL with password from secrets if available"""
    redis_password = read_secret('redis_password', '')
    if redis_password:
        return f"redis://:{redis_password}@redis:6379/{db_number}"
    else:
        return os.environ.get('REDIS_URL', f'redis://127.0.0.1:6379/{db_number}')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_redis_url(0),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'stickforstats',
        'TIMEOUT': 60 * 60 * 24,  # 1 day default timeout
    },
    'embeddings': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_redis_url(1),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'stickforstats:embeddings',
        'TIMEOUT': 60 * 60 * 24 * 7,  # 7 days for embeddings
    },
    'retrieval': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_redis_url(2),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'stickforstats:retrieval',
        'TIMEOUT': 60 * 60 * 24,  # 1 day for retrieval results
    },
    'rag_queries': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_redis_url(3),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'stickforstats:rag_queries',
        'TIMEOUT': 60 * 60 * 3,  # 3 hours for query responses
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_redis_url(4),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'stickforstats:sessions',
        'TIMEOUT': 60 * 60 * 24 * 7,  # 7 days for sessions
    }
}

# Session settings using file-based backend
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = '/tmp/django_sessions'  # Using tmp directory which we've created and set permissions for
# Alternative configurations if needed
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database backend
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'sessions'

# RAG System settings
RAG_SYSTEM = {
    'VECTOR_DB_PATH': os.environ.get('RAG_VECTOR_DB_PATH', BASE_DIR / 'vector_db'),
    'DOCUMENTS_PATH': os.environ.get('RAG_DOCUMENTS_PATH', BASE_DIR / 'documents'),
    'MODEL_NAME': os.environ.get('RAG_MODEL_NAME', 'all-MiniLM-L6-v2'),  # Default to a small model
    'VECTOR_SIZE': int(os.environ.get('RAG_VECTOR_SIZE', 384)),  # Depends on the model
    'CHUNK_SIZE': int(os.environ.get('RAG_CHUNK_SIZE', 300)),
    'CHUNK_OVERLAP': int(os.environ.get('RAG_CHUNK_OVERLAP', 50)),
    'RETRIEVAL_TOP_K': int(os.environ.get('RAG_RETRIEVAL_TOP_K', 5)),
    'API_KEY': os.environ.get('RAG_API_KEY', ''),
    'API_URL': os.environ.get('RAG_API_URL', ''),
    
    # Cache configuration
    'CACHE_ENABLED': os.environ.get('RAG_CACHE_ENABLED', 'True') == 'True',
    'CACHE_EMBEDDINGS': os.environ.get('RAG_CACHE_EMBEDDINGS', 'True') == 'True',
    'CACHE_QUERIES': os.environ.get('RAG_CACHE_QUERIES', 'True') == 'True',
    'EMBEDDING_CACHE_TIMEOUT': int(os.environ.get('RAG_EMBEDDING_CACHE_TIMEOUT', 60 * 60 * 24 * 7)),  # 7 days
    'RETRIEVAL_CACHE_TIMEOUT': int(os.environ.get('RAG_RETRIEVAL_CACHE_TIMEOUT', 60 * 60 * 24)),  # 1 day
    'QUERY_CACHE_TIMEOUT': int(os.environ.get('RAG_QUERY_CACHE_TIMEOUT', 60 * 60 * 3)),  # 3 hours
    'CACHE_STATS_INTERVAL': int(os.environ.get('RAG_CACHE_STATS_INTERVAL', 100)),  # Log stats every 100 operations
    
    'MAX_QUERY_LENGTH': int(os.environ.get('RAG_MAX_QUERY_LENGTH', 1000)),
    'MAX_CONVERSATION_LENGTH': int(os.environ.get('RAG_MAX_CONVERSATION_LENGTH', 20)),
}

# Data Service settings
DATA_SERVICE = {
    'CACHE_TIMEOUT': 3600,  # 1 hour
    'TEMP_DIR': 'temp',
    'ALLOW_CUSTOM_TRANSFORMATIONS': DEBUG,  # Only allow in development
}

# Module registry settings
MODULE_REGISTRY = {
    'AUTODISCOVER_ENABLED': True,
    'MODULES_PATH': 'stickforstats',
}

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
        'confidence_intervals': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'confidence_intervals.performance': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'confidence_intervals.error': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
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