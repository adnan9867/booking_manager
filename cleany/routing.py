from django.urls import re_path, path
from django_private_chat2 import consumers

from cleany.consumer import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:booking_id>', ChatConsumer.as_asgi()),
]