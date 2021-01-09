import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import SyncConsumer, AsyncConsumer

class WriteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.board_room = '123'
        await self.channel_layer.group_add(
            self.board_room,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })
    
    async def websocket_receive(self, event):
        text = event.get('text', None)
        await self.channel_layer.group_send(
            self.board_room,
            {
            "type": "board_message",
            "text": text
            }
        )

    async def board_message(self, event):
        await self.send({
            "type": 'websocket.send',
            'text': event['text']
        })

class AuthConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        

    async def websocket_receive(self, event):

