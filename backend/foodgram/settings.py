import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', default='secret_key')


ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default=['*']).split(' ')  # noqa
# ALLOWED_HOSTS = ('127.0.0.1', 'backend')
# DEBUG = os.getenv('DEBUG', default=False)
DEBUG = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'djoser',
    'drf_yasg',
    'colorfield',
    'rest_framework',
    'rest_framework.authtoken',
    'api',
    'users',
    'recipes',
    'sorl.thumbnail',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default="django.db.backends.postgresql_psycopg2"),  # noqa
        'NAME': os.getenv('DB_NAME', default="foodgram_db"),
        'USER': os.getenv('POSTGRES_USER', default="postgres"),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default="admin"),
        'HOST': os.getenv('DB_HOST', default="localhost"),
        'PORT': os.getenv('DB_PORT', default="5432")
    }
}

'''
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', default="django.db.backends.postgresql_psycopg2"),  # noqa
            'NAME': os.getenv('DB_NAME', default="foodgram_db"),
            'USER': os.getenv('POSTGRES_USER', default="postgres"),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default="admin"),
            'HOST': os.getenv('DB_HOST', default="localhost"),
            'PORT': os.getenv('DB_PORT', default="5432")
        }
    }
'''

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        ('rest_framework.permissions.AllowAny', )
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',  # noqa
    'PAGE_SIZE': 6,
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.IsAuthenticated'],
    },
}


EMAIL_MAX_LENGTH = 254
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
USERNAME_MAX_LENGTH = 150

INGREDIENT_NAME_MAX_LENGTH = 200
INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH = 200
TAG_NAME_MAX_LENGTH = 200
TAG_SLUG_MAX_LENGTH = 200
TAG_COLOR_MAX_LENGTH = 7
RECIPE_NAME_MAX_LENGTH = 200
RECIPE_COOKING_TIME_MIN_LENGTH = 1
INGREDIENT_IN_RECIPE_MIN_LENGTH = 1
