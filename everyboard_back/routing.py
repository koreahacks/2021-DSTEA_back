from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from main.consumers import WriteConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        URLRouter(
            [
                url("write/<str:board_url>/<str:session_id>/", WriteConsumer.as_asgi()),
                # url("delete/", DeleteConsumer.as_asgi()),
                # url("auth_req/", AuthReqConsumer.as_asgi()),
                # url("auth_res/", AuthResConsumer.as_asgi()),
            ]
        )
    )
})
