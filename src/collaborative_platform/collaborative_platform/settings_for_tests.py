from .settings import *

TEST_ENV = 'default'

# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media_for_tests')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'close_reading': {
            'handlers': [],
            'level': 'DEBUG',
        },
        'files_management': {
            'handlers': [],
            'level': 'DEBUG',
        },
        'projects': {
            'handlers': [],
            'level': 'DEBUG',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'long',
        },
    },
    'formatters': {
        'long': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
        },
    },
    'filters': {},
}


TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
