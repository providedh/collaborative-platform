from .settings import *

# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media_for_tests')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ctest',
        'USER': 'ctest',
        'PASSWORD': 'ctest',
        'HOST': "localhost",
        'PORT': '5432',
    }
}
