from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, signals

from django.conf import settings  # for celery 3.xx

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_platform.settings')

app = Celery('collaborative_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')  # for celery 4.3

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()  # for celery 4.3


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass
