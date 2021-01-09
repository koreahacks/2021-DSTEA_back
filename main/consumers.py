import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from .models import *

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


class DeleteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        

    async def websocket_receive(self, event):

class AuthConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        

    async def websocket_receive(self, event):


