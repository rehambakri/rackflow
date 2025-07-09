import json

from asgiref.sync import async_to_sync
from authentication.models import CustomUser
from channels.generic.websocket import WebsocketConsumer

from .models import Notification


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        pass

    def receive(self, text_data):
        pass
