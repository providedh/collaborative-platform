"""
Django settings for collaborative_platform project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""


import os

from datetime import timedelta

from .log_filters import skip_logs_from_certain_modules
from apps.api_vis.enums import TypeChoice


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mg+a43150+*-_tih02!gn8zqcq3^(hp4-ot085^ozu3zcq(u%y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []
ES_HOST = "elasticsearch"
POSTGRES_HOST = 'postgres'
REDIS_HOST = 'redis'

# Application definition

INSTALLED_APPS = [
    'channels',
    'captcha',
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',
    'apps.api_vis',
    'apps.core',
    'apps.files_management',
    'apps.index_and_search',
    'apps.projects',
    'apps.close_reading',
    'apps.dataset_stats',
    'apps.vis_dashboard',
    'apps.nn_disambiguator',
    'apps.help',
    'apps.disambiguator_ui',
    'social_django',
    'django_cleanup',
    # 'django_extensions',  # for SSL on localhost
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'collaborative_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'collaborative_platform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'collaborative_platform',
        'USER': 'collaborative_platform',
        'PASSWORD': 'collapass',
        'HOST': POSTGRES_HOST,
        'PORT': '5432',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "..", "..", "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media')
MEDIA_URL = "/media/"


# Logging
LOGS_ROOT = os.path.join(BASE_DIR, '..', '..', 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'close_reading': {
            'handlers': ['console', 'close_reading_log_file'],
            'level': 'DEBUG',
        },
        'files_management': {
            'handlers': ['console', 'files_management_log_file'],
            'level': 'DEBUG',
        },
        'projects': {
            'handlers': ['console', 'projects_log_file'],
            'level': 'DEBUG',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'long',
        },
        'close_reading_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_ROOT, 'close_reading.log'),
            'formatter': 'long',
            'filters': ['skip_logs_from_certain_modules'],
        },
        'files_management_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_ROOT, 'files_management.log'),
            'formatter': 'long',
        },
        'projects_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_ROOT, 'projects.log'),
            'formatter': 'long',
        }
    },
    'formatters': {
        'long': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'skip_logs_from_certain_modules': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_logs_from_certain_modules,
        },
    },
}


# ReCaptcha keys
# Comment this settings for local testing
# https://pypi.org/project/django-recaptcha/#installation
RECAPTCHA_PUBLIC_KEY = 'put_public_key_here'
RECAPTCHA_PRIVATE_KEY = 'put_private_key_here'

# Uncomment this setting for local testing
# https://pypi.org/project/django-recaptcha/#local-development-and-functional-testing
# SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']


# For WebSockets
ASGI_APPLICATION = 'collaborative_platform.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, 6379)],
        }
    }
}


# For periodic tasks
CELERY_BROKER_URL = 'redis://{}:6379'.format(REDIS_HOST)
CELERY_RESULT_BACKEND = 'redis://{}:6379'.format(REDIS_HOST)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'prune-presence': {
        'task': 'close_reading.tasks.prune_presence',
        'schedule': timedelta(seconds=60),
    },
    'prune-orphaned-annotating-xml-contents': {
        'task': 'close_reading.tasks.prune_orphaned_annotating_body_contents',
        'schedule': timedelta(seconds=120),
    },
    'run_queued_nn_disambiguation_tasks': {
        'task': 'nn_disambiguator.run_queued_tasks',
        'schedule': timedelta(seconds=5)
    }
}


# For getting site url from database
# https://docs.djangoproject.com/en/2.2/ref/contrib/sites/#enabling-the-sites-framework
SITE_ID = 1


# For social-auth-app-django
# https://python-social-auth-docs.readthedocs.io/en/latest/configuration/django.html
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.orcid.ORCIDOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details'
)

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'index'

SOCIAL_AUTH_ORCID_KEY = 'put client ID here'
SOCIAL_AUTH_ORCID_SECRET = 'put secret key here'

SOCIAL_AUTH_FACEBOOK_KEY = 'put client ID here'
SOCIAL_AUTH_FACEBOOK_SECRET = 'put secret key here'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email',
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'put client ID here'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'put secret key here'

SOCIAL_AUTH_LOGIN_ERROR_URL = 'settings'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


# XML namespaces
XML_NAMESPACES = {
    'default': 'http://www.tei-c.org/ns/1.0',
    'tei': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xi': 'http://www.w3.org/2001/XInclude',
}

NS_MAP = {
    None: XML_NAMESPACES['default'],
    'xml': XML_NAMESPACES['xml'],
    # 'xi': XML_NAMESPACES['xi']
}


# Entities structure
DEFAULT_ENTITIES = {
    'person': {
        'properties': {
            'sex': {
                'type': TypeChoice.str,
                'xpath': '@sex',
            },
            'age': {
                'type': TypeChoice.str,
                'xpath': '@age',
            },
            'forename': {
                'type': TypeChoice.str,
                'xpath': './default:persName/default:forename/text()'
            },
            'surname': {
                'type': TypeChoice.str,
                'xpath': './default:persName/default:surname/text()',
            },
            'occupation': {
                'type': TypeChoice.str,
                'xpath': './default:occupation/text()',
            },
            'birth': {
                'type': TypeChoice.date,
                'xpath': './default:birth/@when',
            },
            'death': {
                'type': TypeChoice.date,
                'xpath': './default:death/@when',
            },
            'name': {
                'type': TypeChoice.str,
                'xpath': './default:name/text()',
            },
        },
        'listable': True,
        'text_tag': 'name',
        'list_tag': 'listPerson',
        'color': '#ff7f00',
        'icon': r'\f007',
        'unifiable': True,
    },
    'event': {
        'properties': {
            'name': {
                'type': TypeChoice.str,
                'xpath': './text()',
            },
        },
        'listable': True,
        'text_tag': 'name',
        'list_tag': 'listEvent',
        'color': '#cecece',
        'icon': r'\f274',
        'unifiable': True,
    },
    'org': {
        'properties': {
            'name': {
                'type': TypeChoice.str,
                'xpath': './text()',
            },
        },
        'listable': True,
        'text_tag': 'name',
        'list_tag': 'listOrg',
        'color': '#b4edfc',
        'icon': r'\f1ad',
        'unifiable': True,
    },
    'object': {
        'properties': {
            'name': {
                'type': TypeChoice.str,
                'xpath': './text()',
            },
        },
        'listable': True,
        'text_tag': 'name',
        'list_tag': 'listObject',
        'color': '#b4d38d',
        'icon': r'\f466',
        'unifiable': True,
    },
    'place': {
        'properties': {
            'country': {
                'type': TypeChoice.str,
                'xpath': './default:country/text()',
            },
            'settlement': {
                'type': TypeChoice.str,
                'xpath': './default:settlement/text()',
            },
            'geo': {
                'type': TypeChoice.Point,
                'xpath': './default:location/default:geo/text()',
            },
            'name': {
                'type': TypeChoice.str,
                'xpath': './default:placeName/default:name/text()'
            },
        },
        'listable': True,
        'text_tag': 'name',
        'list_tag': 'listPlace',
        'color': '#204191',
        'icon': r'\f279',
        'unifiable': True,
    },
    'date': {
        'properties': {
            'when': {
                'type': TypeChoice.date,
                'xpath': '@when',
            },
            'name': {
                'type': TypeChoice.str,
                'xpath': './text()'
            },
        },
        'listable': False,
        'text_tag': 'date',
        'list_tag': None,
        'color': '#868788',
        'icon': r'\f073',
        'unifiable': False,
    },
    'time': {
        'properties': {
            'when': {
                'type': TypeChoice.time,
                'xpath': '@when',
            },
            'name': {
                'type': TypeChoice.str,
                'xpath': './text()'
            }
        },
        'listable': False,
        'text_tag': 'time',
        'list_tag': None,
        'color': '#eab9e4',
        'icon': r'\f017',
        'unifiable': False,
    },
}

CUSTOM_ENTITY = {
    'properties': {
        'name': {
            'type': TypeChoice.str,
            'xpath': './text()'
        }
    },
    'listable': True,
    'text_tag': 'name',
}

ADDITIONAL_USABLE_TAGS = ['certainty', 'name', 'seg']

ADDITIONAL_XML_ID_BASES = ['annotator']


ANONYMOUS_USER_ID = 1
