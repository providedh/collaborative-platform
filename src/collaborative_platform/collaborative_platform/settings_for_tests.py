from .settings import *

# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media_for_tests')

DATABASES['default']['HOST'] = "localhost"
DATABASES['default']['USER'] = "postgres"
DATABASES['default']['PASSWORD'] = ""
# {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'postgres',
#         # 'USER': 'postgres',
#         # 'PASSWORD': '',
#         'HOST': "localhost",
#         'PORT': '5432',
#     }
# }
