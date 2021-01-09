from django.conf.urls import url
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import OriginValidator, AllowedHostsOriginValidator
from main.consumers import WriteConsumer
from main.consumers import DeleteConsumer
from main.consumers import AuthConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        URLRouter(
            [
                url("write/<str:board_url>/<str:session_id>", WriteConsumer.as_asgi()),
                url("delete/<str:board_url>/<str:session_id>", DeleteConsumer.as_asgi()),
                url("auth/<str:board_url>/<str:session_id>", AuthConsumer.as_asgi()),
            ]
        )
    )
})
