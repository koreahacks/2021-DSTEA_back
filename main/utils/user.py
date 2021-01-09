import uuid1
import random

from main.models import User
from main.utils.common import Status, Message

with open("main/fruits.txt", "r") as f:
    fruit_list = f.read().split('\n')

def create_user(request):
    if request.session.get('id') is None: # First Access
        try:
            user = User(session_id=str(uuid1.uuid1()),
                        nickname=random.sample(animal_list, 1)[0] # 추후 수정 필요
                        )
            user.save()
            
        except Exception as e:
            return Message(Status.INTERNAL_ERROR, f'Internal server error, {e}')
        
        return Message(Status.SUCCESS, user=user)

    else:
        return Message(Status.BAD_REQUEST, 'User already exists')