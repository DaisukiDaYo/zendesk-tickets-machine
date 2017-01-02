from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ztm',
        'USER': 'ztm',
        'PASSWORD': os.environ.get('ZTM_DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('ZTM_DATABASE_HOST', ''),
        'PORT': '5432',
    }
}
