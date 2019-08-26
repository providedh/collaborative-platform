"""
WSGI config for collaborative_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from elasticsearch_dsl.connections import create_connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_platform.settings')

create_connection()

application = get_wsgi_application()
