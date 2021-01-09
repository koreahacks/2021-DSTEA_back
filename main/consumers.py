import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import SyncConsumer, AsyncConsumer

from main.models import Board, User

AUTHRES = 'res'
AUTHREQ = 'req'

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
        self.board_url = self.scope['url_route']['kwargs']['board_url']
        self.channel_name = self.scope['url_route']['kwargs']['session_id']

        await self.channel_layer.group_add(
            f'auth-{self.board_url}',
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        action = event.get('action', None)

        if action == AUTHREQ:
            await self.channel_layer.group_send(
                f'auth-{self.board_url}',
                {
                    "type": "auth_request",
                    "session_id": self.channel_name,
                    "admin_id": 
                }
            )


        elif action == AUTHRES:
            accept = event.get('accept', None)
            session_id = event.get('session_id', None)
            await self.channel_layer.group_send(
                f'auth-{self.board_url}',
                {
                    "type": "auth_response",
                    "session_id": session_id,
                    "accept": accept
                }
            )


    async def auth_request(self, event):
        if event['admin_id'] == self.channel_name:
            await self.send({
                "type": 'websocket.send',
                'session_id': event['session_id']
            })
            
    async def auth_response(self, event):
        if event['session_id'] == self.channel_name:
            await self.send({
                "text": event['accept'],
            })

