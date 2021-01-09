import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from main.models import Path, Board, User

AUTHRES = 'res'
AUTHREQ = 'req'

class WriteConsumer(AsyncConsumer):
    @database_sync_to_async
    def save_path(self, board_url, text):
        board = Board.objects.get(board_url=board_url)
        path = Path(
            path_id = text['path_id'],
            board = board,
            page_id = text['page'],
            is_public = text['is_public'],
            color = text['attr']
        )
        path.save()

    @database_sync_to_async
    def update_user(self, session_id, channel_name):
        try:
            user = User.objects.get(session_id=session_id)
            user.channel_name = channel_name
            user.save()
        except:
            return
    
    @database_sync_to_async
    def update_path(self, path_id, pos):
        path = Path(path_id = path_id)
        path.data = pos
        path.save()

    async def websocket_connect(self, event):
        board_url = self.scope['url_route']['kwargs']['board_url']
        session_id = self.scope['url_route']['kwargs']['session_id']

        await self.update_user(session_id, self.channel_name)
        
        await self.channel_layer.group_add(
            board_url,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })
    
    async def websocket_receive(self, event):
        board_url = self.scope['url_route']['kwargs']['board_url']
        session_id = self.scope['url_route']['kwargs']['session_id']

        text = json.loads(event['text'])

        if text['status'] == 'start':
            await self.save_path(board_url, text)

        if text['status'] == 'draw':
            path = await database_sync_to_async(Path.objects.get)(path_id=text['path_id'])
            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "board_message",
                    "info": path.info(),
                    "pos": text['pos'],
                }
            )

        if text['status'] == 'end':
            await self.update_path(text['path_id'], text['pos'])

    async def board_message(self, event):
        data = json.dumps({
            'path_id': event['info']['path'],
            'is_public': event['info']['is_public'],
            'page': event['info']['page'],
            'attr': event['info']['attr'],
            'pos': event['pos']
        })
        await self.send({
            'type': 'websocket.send',
            'text': data,
        })

    async def websocket_disconnect(self, event):
        print('disconnected')

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
