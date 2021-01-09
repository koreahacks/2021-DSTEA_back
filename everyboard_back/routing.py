from django.conf.urls import url
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import OriginValidator, AllowedHostsOriginValidator
from main.consumers import WriteConsumer, DeleteConsumer, AuthReqConsumer, AuthResConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        URLRouter(
            [
                url("<board_url>/write/", WriteConsumer.as_asgi()),
                url("delete/", DeleteConsumer.as_asgi()),
                url("auth_req/", AuthReqConsumer.as_asgi()),
                url("auth_res/", AuthResConsumer.as_asgi()),
            ]
        )
    )
})
