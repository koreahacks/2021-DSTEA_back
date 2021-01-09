import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from .models import *
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async



from main.models import Board, User

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

    async def websocket_connect(self, event):
        # board_url = self.scope['url_route']['kwargs']['board_url']
        # session_id = self.scope['url_route']['kwargs']['session_id']
        # try:
        #     board = Board.objects.get(board_url=text['board'])
        #     user = User.objects.get(session_id=text['user'])

        # except Exception as e:
        #     await self.send({
        #         "error_msg": e
        #     })
        # await self.update_user(session_id, self.channel_name)
        # print(board_url)
        print(self.channel_name)
        print(self.channel_layer)
        await self.channel_layer.group_add(
            'asdf',
            self.channel_name
        )            
        await self.channel_layer.group_send(
            'asdf',
            {
                "type": "board_message",
                # "info": path.info(),
                "pos": '123123'
            }
        )
        await self.send({
            "type": "websocket.accept"
        })
    
    async def websocket_receive(self, event):
        # board_url = self.scope['url_route']['kwargs']['board_url']
        # session_id = self.scope['url_route']['kwargs']['session_id']

        text = json.loads(event['text'])
        print(text)
        print(type(text))
        # if text['status'] == 'start':
        #     await self.save_path(board_url, text)
            
        if text['status'] == 'draw':
            print(self.channel_layer)
            # path = await database_sync_to_async(Path.objects.get)(path_id=text['path_id'])
            await self.channel_layer.group_send(
                'asdf',
                {
                    "type": "board_message",
                    # "info": path.info(),
                    "pos": '123123'
                }
            )
        
        elif text['status'] == 'end':
            pass
            

    async def board_message(self, event):
        print({
            'type': 'websocket.send',
            # 'path_id': event['info']['path'],
            # 'is_public': event['info']['is_public'],
            # 'page': event['info']['page'],
            # 'attr': event['info']['attr'],
            'pos': event['pos']
        })
        await self.send({
            'type': 'websocket.send',
            # 'path_id': event['info']['path'],
            # 'is_public': event['info']['is_public'],
            # 'page': event['info']['page'],
            # 'attr': event['info']['attr'],
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
