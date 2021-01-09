from django.urls import path
from main.consumers import WriteConsumer

websocket_urlpatterns = [
    path("write/", WriteConsumer.as_asgi()),
]