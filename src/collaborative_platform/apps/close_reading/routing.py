from channels.routing import URLRouter
from django.conf.urls import url

from . import consumers

url_router = URLRouter([
    url(r'(?P<room_name>[^/]+)/$', consumers.AnnotatorConsumer)
])
