from channels.routing import URLRouter
from django.conf.urls import url
from channels.security.websocket import OriginValidator
from main.consumers import WriteConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        URLRouter(
            [
                url("write/", WriteConsumer.as_asgi()),
                url("delete/", DeleteConsumer.as_asgi()),
                url("auth_req/", AuthReqConsumer.as_asgi()),
                url("auth_res/", AuthResConsumer.as_asgi()),
            ]
        )
    )
})
