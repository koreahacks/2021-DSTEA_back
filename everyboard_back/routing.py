from django.urls import path
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import OriginValidator, AllowedHostsOriginValidator

from main.consumers import WriteConsumer
# from main.consumers import DeleteConsumer
from main.consumers import AuthConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path("write/", WriteConsumer.as_asgi()),
            # path("auth/<str:board_url>/<str:session_id>/", AuthConsumer.as_asgi()),
        ])
    )
})
