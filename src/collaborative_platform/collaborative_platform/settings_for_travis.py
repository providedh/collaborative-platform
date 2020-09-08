from .settings_for_tests import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': "localhost",
        'PORT': '5432',
    }
}

REDIS_HOST = "localhost"
CELERY_BROKER_URL = 'redis://{}:6379'.format(REDIS_HOST)
CELERY_RESULT_BACKEND = 'redis://{}:6379'.format(REDIS_HOST)
