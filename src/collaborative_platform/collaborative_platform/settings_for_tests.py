from .settings import *

# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media_for_tests')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'annotator': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'upload': {
            'handlers': ['console'],
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
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'filters': {},
}
