import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from .models import *

from main.models import Board, User

AUTHRES = 'res'
AUTHREQ = 'req'

class WriteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        board_url = self.scope['url_route']['kwargs']['board_url']
        session_id = self.scope['url_route']['kwargs']['session_id']
        try:
            board = Board.objects.get(board_url=text['board'])
            user = User.objects.get(session_id=text['user'])

        except Exception as e:
            await self.send({
                "error_msg": e
            })

        await self.channel_layer.group_add(
            board_url,
            session_id
        )
        await self.send({
            "type": "websocket.accept"
        })
    
    async def websocket_receive(self, event):
        board_url = self.scope['url_route']['kwargs']['board_url']
        session_id = self.scope['url_route']['kwargs']['session_id']
        text = json.loads(event['text'])
        if text['status'] == 'start':
            board = Board.objects.get(board_url=board_url)
            path = Path()
            path.path_id = text['path']['id']
            path.board = board
            path.page_id = text['page_id']
            path.is_public = text['is_public']
            path.color = text['path']['attr']['color']
            path.save()
            
        elif text['status'] == 'draw':
            path = Path.objects.get(path_id=text['path_id'])
            
            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "board_message",
                    "info": path.info(),
                    "pos": text['pos']
                }
            )
        
        elif text['status'] == 'end':
            pass
            

    async def board_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'info': event['info'],
            'pos': event['pos']
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
            board = Board.objects.get(board_url=self.board_url)
            admin_id = board.admin_id
            await self.channel_layer.group_send(
                f'auth-{self.board_url}',
                {
                    "type": "auth_request",
                    "session_id": self.channel_name,
                    "admin_id": admin_id
                }
            )

        elif action == AUTHRES:
            accept = event.get('accept', None)
            session_id = event.get('session_id', None)

            if accept:
                user = User.objects.get(session_id=session_id)
                user.auth_write = True
                user.save()

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
                "accept": event['accept'],
            })

