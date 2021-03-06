import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from main.models import Path, Board, User

AUTHRES = 'res'
AUTHREQ = 'req'
AUTHUSER = 'user'

class WriteConsumer(AsyncConsumer):
    @database_sync_to_async
    def save_path(self, board_url, text):
        board = Board.objects.get(board_url=board_url)
        path = Path(
            path_id = text['path_id'],
            board = board,
            page_id = text['page'],
            is_public = text['is_public'],
            color = text['attr'],
            data = text['pos']
        )
        path.save()
        return path
    
    @database_sync_to_async
    def update_path(self, path_id, pos):
        path = Path.objects.get(path_id = path_id)
        path = Path(
            path_id = text['path_id'],
            board = board,
            page_id = text['page'],
            is_public = text['is_public'],
            color = text['attr']
        )
        path.data = str(pos)
        path.save()

    @database_sync_to_async
    def delete_path(self, path_id):
        try:
            path = Path.objects.get(path_id=path_id)
            page = path.page_id
            path.delete()
            return page
        except:
            return None

    async def websocket_connect(self, event):
        board_url = self.scope['url_route']['kwargs']['board_url']
        self.session_id = self.scope['url_route']['kwargs']['session_id']

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
            
            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "write_message",
                    "data": {
                        'path':text['path_id'],
                        'page':text['page'],
                        'is_public': text['is_public'],
                        'attr': text['attr']
                    },
                    'session_id':session_id,
                    "status": 'start'
                }
            ) 

        elif text['status'] == 'draw':
            #path = await database_sync_to_async(Path.objects.get)(path_id=text['path_id'])
            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "write_message",
                    "data": {
                        'path': text['path_id'],
                        'page': text['page'],
                    },
                    'session_id':session_id,
                    "pos": text['pos'],
                    "status": 'draw'
                }
            )

        elif text['status'] == 'end':
            new_path = await self.save_path(board_url, text)
            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "write_message",
                    "data": new_path.info(),
                    'session_id':session_id,
                    "status": 'end'
                }
            )            

        elif text['status'] == 'delete':
            page = await self.delete_path(text['path_id'])

            await self.channel_layer.group_send(
                board_url,
                {
                    "type": "delete_message",
                    "data": {'page': page, 'path_id': text['path_id']}
                }
            )

    async def write_message(self, event):
        data = json.dumps({
                'status': event['status'],
                'path_id': event['data'].get('path'),
                'is_public': event['data'].get('is_public'),
                'page': event['data'].get('page'),
                'attr': event['data'].get('attr'),
                'pos': event.get('pos')
            })
        print(self.session_id, event.get('session_id'))
        if self.session_id == event.get('session_id'):
            return
        await self.send({
                'type': 'websocket.send',
                'text': data,
            })

    async def delete_message(self, event):
        data = json.dumps({
            'status': 'delete',
            'page': page,
            'path_id': path_id
        })
        await self.send({
            'type': 'websocket.send',
            'text': data,
        })

    async def websocket_disconnect(self, event):
        print('disconnected')

class AuthConsumer(AsyncConsumer):
    @database_sync_to_async
    def get_board(self, board_url):
        return Board.objects.get(board_url=board_url)

    @database_sync_to_async
    def auth_user(self, session_id):
        user = User.objects.get(session_id=session_id)
        user.auth_write = True
        user.save()

    @database_sync_to_async
    def update_user(self, session_id, channel_name):
        try:
            user = User.objects.get(session_id=session_id)
            user.channel_name = channel_name
            user.save()
        except:
            return

    @database_sync_to_async
    def check_auth(self, board_url, user):
        board = Board.objects.get(board_url=str(board_url))
        if board.admin_id == user.session_id:
            auth = 0
        elif user.auth_write == True:
            auth = 1
        else:
            auth = 2
        return auth

    async def websocket_connect(self, event):
        self.board_url = self.scope['url_route']['kwargs']['board_url']
        self.session_id = self.scope['url_route']['kwargs']['session_id']

        await self.update_user(self.session_id, self.channel_name)

        await self.channel_layer.group_add(
            f'auth-{self.board_url}',
            self.channel_name
        )

        user = await database_sync_to_async(User.objects.get)(session_id=session_id)
        auth = await self.check_auth(board_url, user)

        await self.channel_layer.group_send(
            f'auth-{self.board_url}',
            {
                "type": "userlist",
                "text": {"nickname": user.nickname, "auth": auth},
            }
        )

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        text = json.loads(event['text'])
        action = text.get('action', None)

        if action == AUTHREQ:
            board = await self.get_board(self.board_url)
            admin_id = board.admin_id

            await self.channel_layer.group_send(
                f'auth-{self.board_url}',
                {
                    "type": "auth_request",
                    "session_id": self.session_id,
                    "admin_id": admin_id
                }
            )

        elif action == AUTHRES:
            accept = text.get('accept', None)
            session_id = text.get('session_id', None)

            if accept:
                await self.auth_user(session_id)

            await self.channel_layer.group_send(
                f'auth-{self.board_url}',
                {
                    "type": "auth_response",
                    "session_id": session_id,
                    "accept": accept
                }
            )

    async def auth_request(self, event):
        if self.session_id == event['admin_id']:
            await self.send({
                "type": 'websocket.send',
                'text': json.dumps({'session_id': event['session_id']})
            })
            
    async def auth_response(self, event):
        if self.session_id == event['session_id']:
            await self.send({
                "type": 'websocket.send',
                "text": json.dumps({'accept':event['accept']}),
            })

    async def userlist(self, event):
        data = json.dumps(event['text'])
        await self.send({
            "type": 'websocket.send',
            "text": data
        })
