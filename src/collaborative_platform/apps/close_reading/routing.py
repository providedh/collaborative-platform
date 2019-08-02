from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^websocket/(?P<room_name>[^/]+)/$', consumers.AnnotatorConsumer),
]
