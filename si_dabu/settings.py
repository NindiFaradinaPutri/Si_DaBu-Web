"""
Django settings for silatama project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
#url yang akan dipanggil
STATIC_URL = '/static/'

#Tempat dimana dikumpulkan static
STATIC_ROOT = os.path.join(BASE_DIR,'static')

#Alternatif folder yang akan dicek ketika static dipanggil
STATICFILES_DIRS = [os.path.join(BASE_DIR,'app','static'),
                    ]

# Media files (CSS, JavaScript, Images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'app','static','media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('ABSENSI_EVENT_SECRET_KEY'),

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['localhost',
                 '127.0.0.1',
                 '192.168.1.92',
                 'presengo.test',
                 '192.168.1.191']


# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    # Add your apps here to enable them
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'app',
    'banner',
    'authentication',
    # 'complaint',
    'event',
    # 'finance',
    'form',
    'gallery',
    # 'information',
    # 'news',
    'portfolio',
    'profile',
    # 'team',
    'participant.apps.ParticipantConfig',

    'django_tables2',
    'django_filters',
    'widget_tweaks',
    'rest_framework.authtoken',
    'rest_framework',
    'django_crontab',
    'captcha',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 604800
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False

ROOT_URLCONF = 'si_dabu.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
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
                'django.template.context_processors.media',
                'app.context_processors.google_map_key',
                'app.context_processors.posts',
            ],
        },
    },
]

AUTH_USER_MODEL = 'authentication.UserData'

WSGI_APPLICATION = 'si_dabu.wsgi.application'
# WSGI_APPLICATION = 'emasjid.wsgi.application'
#ASGI_APPLICATION = 'nganggur.asgi.application'

#reCAPTCHA
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
# RECAPTCHA_PUBLIC_KEY = os.environ.get('ABSENSI_EVENT_RECHA_PBC_KEY')
# RECAPTCHA_PRIVATE_KEY = os.environ.get('ABSENSI_EVENT_RECHA_PVT_KEY')

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('ABSENSI_EVENT_PGSQL_DB_ENGINEE'),
        'NAME': os.environ.get('ABSENSI_EVENT_PGSQL_DB'),
        'USER': os.environ.get('ABSENSI_EVENT_PGSQL_DB_USER'),
        'PASSWORD': os.environ.get('ABSENSI_EVENT_PGSQL_DB_PASS'),
        'HOST': '127.0.0.1',
        'PORT':'5432',
    }
    
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'utils.utils.CustomUserAttributeSimilarityValidator',
    },
    {
        'NAME': 'utils.utils.CustomMinimumLengthValidator',
        'OPTIONS':{
            'min_length':8,
            }
    },
    {
        'NAME': 'utils.utils.CustomCommonPasswordValidator',
    },
    {
        'NAME': 'utils.utils.CustomNumericPasswordValidator',
    },
    {
        'NAME':'utils.utils.NumberValidator',
    },
    {
        'NAME':'utils.utils.UppercaseValidator',
    },
    {
        'NAME':'utils.utils.LowercaseValidator',
    },
]

#setup data upload max for field
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'id-ID'
TIME_ZONE = 'Asia/Makassar'
USE_I18N = True
USE_L10N = True #SET TRUE IF WANT GLOBAL OVERRIDE LOCAL
USE_TZ = True

USE_DECIMAL_SEPARATOR = True
DECIMAL_SEPARATOR = ","
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = "."

DATE_FORMAT = 'Y-m-d'
HTML_DATE_FORMAT = 'yyyy-mm-dd'
DATETIME_FORMAT = 'Y-m-d H:i:s'
HTML_DATETIME_FORMAT = 'yyyy-mm-dd HH:mm:ss'
TIME_FORMAT = 'H:i:s'
HTML_TIME_FORMAT = 'HH:mm:ss'

DATE_INPUT_FORMATS = ['%Y/%m/%d','%Y-%m-%d','%d-%m-%Y','%d/%m/%Y']

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
]

TIME_INPUT_FORMATS = [
    '%H:%M:%S','%H:%M',
    ]

LOGOUT_REDIRECT_URL = 'home/'

CSRF_USE_SESSIONS = True
#Protect CSRF
CSRF_FAILURE_VIEW = 'views.fe_views.csrf_failure'

#KEY FOR GOOGLE MAPS
RSAD_GOOGLE_MAP_KEY = os.environ.get('ABSENSI_EVENT_GOOGLE_MAP_KEY')

#EMAIL CONF
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('ABSENSI_EVENT_EMAIL_ID') 
EMAIL_HOST_PASSWORD = os.environ.get('ABSENSI_EVENT_EMAIL_PASS') 

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}

MAX_UPLOAD_SIZE = 10000000 #setting size per bytes
VIDEO_UPLOAD_SIZE = 100000000 

FILE_UPLOAD_PERMISSIONS = 0o774

CRONTAB_COMMAND_SUFFIX = '2>&1'

CRONJOBS = [
    ('0 0 * * SAT', 'app.crons.update_week_journal', '>> /var/log/cron/update_week_journal.log'),
]

#CHANNEL_LAYERS = {
#    'default': {
#        'BACKEND': 'channels_redis.core.RedisChannelLayer',
#        'CONFIG': {
#            'hosts': [(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))],
#        },
#    },
#}