from unipath import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).ancestor(3)
SRC_DIR = BASE_DIR.child('src')


TESTING = False
DEBUG = config('DEBUG', cast=bool)
SECRET_KEY = config('SECRET_KEY')
PRODUCTION = config('PRODUCTION', default=False)

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True


INSTALLED_APPS = [
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'django_extensions',
    'corsheaders',
    'django_rq',
    'storages',
    'src.api',
    'src.core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]


ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates')],
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.child("static")]
STATICFILES_STORAGE = config('STATICFILES_STORAGE', default='whitenoise.django.GzipManifestStaticFilesStorage')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10 MB


if PRODUCTION:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_HOST = config('AWS_S3_HOST')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    S3_USE_SIGV4 = True

    S3_URL = '{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
    MEDIA_URL = S3_URL

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

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


LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Django RQ
REDIS_URL = config('REDIS_URL', default='redis://localhost:50002')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DB': 0,
        'DEFAULT_TIMEOUT': 5000,
    },
}


# Admin config
SUIT_CONFIG = {
    'ADMIN_NAME': 'Bienal Art Analyser',
}


# IBM Watson Visual Recognition Config
IBM_WATSON_VISUAL_RECOG_VERSION = '2018-03-19'
IBM_IAM_API_KEY = config('IBM_IAM_API_KEY', default='missing_key')
GOOGLE_VISION_API_KEY = config('GOOGLE_VISION_API_KEY', default='missing_key')
AZURE_VISION_API_KEY = config('AZURE_VISION_API_KEY', default='missing_key')


import django_heroku
django_heroku.settings(locals())
