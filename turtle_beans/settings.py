import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ti3lq+q6cg_*b3)km9dv%zobe5bf4%v%2+a6i$i)ouwz7*8z@m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = [
#     '10.13.228.157', 'localhost', '127.0.0.1', '52.77.110.38',
#     'turtlebeans-api.tersesoft.com', '*'
# ]
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '52.77.110.38', '*']
SITE_DOMAIN = 'localhost:8000'
# SITE_DOMAIN = 'turtlebeans-api.tersesoft.com'

# Application definition

INSTALLED_APPS = [
    'jet.dashboard', 'jet', 'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles',
    'django_extensions', 'rest_framework', 'rest_framework.authtoken',
    'corsheaders', 'phonenumber_field', 'fcm_django', 'sslserver', 'imagekit',
    
    'apps.accounts',
    'apps.coffee', 
    'apps.orders',
    'apps.contacts',
    'apps.coupon_code', 'apps.notifications', 'apps.version','rest_framework_swagger'
   
]

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTH_USER_MODEL = 'accounts.EmailUser'
LOGIN_REDIRECT_URL = '/api/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@turtlebeans.com'
EMAIL_HOST_PASSWORD = '70eba459e7b52f70a6588ee18f7aa518'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = 'shubham@tersesoft.com'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'turtle_beans.urls'

CSRF_TRUSTED_ORIGINS = [
    'turtlebeans-api.tersesoft.com', 'http://localhost:8080/',
    'http://localhost:8080', 'localhost:8080', 'https://localhost:8080',
    'http://localhost:8100/'
]
#
# CORS_REPLACE_HTTPS_REFERER = True
#
# CSRF_COOKIE_DOMAIN = 'turtlebeans-api.tersesoft.com'
#
# CORS_ORIGIN_WHITELIST = ('https://turtlebeans-api.tersesoft.com/',
#                          'turtlebeans-api.tersesoft.com',
#                          'http://localhost:8080/'
#                          'http://localhost:8080', 'localhost:8000',
#                          'http://127.0.0.1:8000',
#                          'http://127.0.0.1:8000/')

CORS_ORIGIN_WHITELIST = ('http://localhost:8100/')

from apps import accounts
TEMPLATES = [
    {
        'BACKEND':
        'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'turtle_beans', 'templates'),
            os.path.join(accounts.__path__[0], 'templates'),
        ],
        'APP_DIRS':
        True,
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

AUTHENTICATION_BACKENDS = (
    'apps.accounts.authentication.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES':
    ('rest_framework.renderers.JSONRenderer',
     'rest_framework.renderers.BrowsableAPIRenderer'),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ),
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'apps.accounts.renderers.CustomJSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # ],
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE':
    5,
}

WSGI_APPLICATION = 'turtle_beans.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'turtle_beans',
        'USER': 'snj',
        'PASSWORD': 'terse@123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}




# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME':'turt',
#         'USER':'root',
#         'PASSWORD':'snj',
#         'PORT':3306,
#         'HOST':'127.0.0.1',
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#django-paypal settings
PAYPAL_RECEIVER_EMAIL = 'marc@turtlebeans.com'
PAYPAL_TEST = True

# Marc's Paypal
PAYPAL_CLIENT_ID = 'AYAoXtMLDYcCWngBhooKlR2Stgiehxux5BXTONicep1CP_62X2u3RD3kwbYmWIatBL8Sx_y1srFBkRlg'
PAYPAL_SECRET_KEY = 'EClLx6yrmokx_PIslQpltqpksONdyVhRxqWdCzyl3aVcXCmi-jYfDdJnVQ9XdFJfAld7q5giHbp_TOO5'

#Vaibhav/s Paypal
# PAYPAL_CLIENT_ID = 'AWeW_CFnMSFsz3LSUzZ6MwW-rGgGtpfcLl7eHHREK3Zcc7NCZMzFLXa9_cXpezAOdMsns2hiEChWOqnD'
# PAYPAL_SECRET_KEY = 'EJVZBwjDjNYaF7PqSXUAu1WqbhtWylwpWxqATby_AshqGlIbyplZGpBOq3BnAzehIlcQeYmlShzA45nS'

#Marc's Credentials
BRAINTREE_MERCHANT_ID = '5zvc7dbkz9nftry6'
BRAINTREE_PUBLIC_KEY = 'pz24b4bsf63pmb5v'
BRAINTREE_PRIVATE_KEY = '26028295c2987f7b7a4562edfaee5b02'

#Vaibhav's Credentials
# BRAINTREE_MERCHANT_ID = 'fhmc6xvj92766hxq'
# BRAINTREE_PUBLIC_KEY = 'psxpvfkv4sd7pgxb'
# BRAINTREE_PRIVATE_KEY = 'b515db93f8a6735d96a340e762741028'

#vijendra's Credentials
# BRAINTREE_MERCHANT_ID = 'pn6fjqp5f8grfkd7'
# BRAINTREE_PUBLIC_KEY = '2j3nxfskxmxzzt3b'
# BRAINTREE_PRIVATE_KEY = '54fedc6f0b12241cd02973c81e2ea6ed'

COF_DESTINATION_ADDRESS = '3PQrxazghZxJmAoLWczjBGpD4hs6gsv7rHq'

FCM_WEB_API_KEY = 'AIzaSyBwRKOMDoD5Vfw1bvMTyOdUwP2n_QNi5FA'

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY":
    "AAAAoJJ6FyA:APA91bHhyN4rPdZdx-tlz6cjNHemnis7AJFC60ExJJEsq50HEiauX9gI8Ns2ebO0kN1kL0c5oMTtuzlXQRCJM7edLSb_UsRsmymzGW1fYTPNxTYoKLcH69MrgwR3y-37eWvbqyAIdNSM",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'turtle_beans', 'templates')
STATIC_ROOT = "/home/snj/Documents/dev/turtlebeans-backend/turtle_beans/static/"

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/snj/Documents/dev/turtlebeans-backend/media/'

GRAPH_MODELS = {'all_applcations': True, 'group_models': True}
