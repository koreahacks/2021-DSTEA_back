from django.conf.urls import url
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import OriginValidator, AllowedHostsOriginValidator
from main.consumers import WriteConsumer#, DeleteConsumer, AuthReqConsumer, AuthResConsumer

import main.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
                main.routing.websocket_urlpatterns
                # url("write/<str:board_url>/<str:session_id>/", WriteConsumer.as_asgi()),
                # url("delete/", DeleteConsumer.as_asgi()),
                # url("auth_req/", AuthReqConsumer.as_asgi()),
                # url("auth_res/", AuthResConsumer.as_asgi()),
        )
    )
})
