from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/(?P<user_slug1>\w+)/(?P<user_slug2>\w+)/$", consumers.GameConsumer.as_asgi()),
    re_path(r"(?P<lobby_name>\w+)/$", consumers.LobbyConsumer.as_asgi()),
]