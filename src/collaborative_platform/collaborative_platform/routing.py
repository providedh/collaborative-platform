# FOR CHANNELS 1
# from channels.routing import route
# from apps.close_reading.consumers import ws_connect, ws_disconnect, ws_message
#
# channel_routing = [
#     route('websocket.connect', ws_connect),
#     route('websocket.disconnect', ws_disconnect),
#     route("websocket.receive", ws_message),
# ]

# FOR CHANNELS 2
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import apps.close_reading.routing
import apps.poetry_analysis.routing
from django.conf.urls import url

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r"^ws/close_reading/", apps.close_reading.routing.url_router),
            url(r"^ws/poetry_analysis/", apps.poetry_analysis.routing.url_router),
        ])
    )
})
