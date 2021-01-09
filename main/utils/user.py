import uuid1
import random

from main.models import User
from main.utils.common import Status, Message, is_success

with open("main/animals.txt", "r") as f:
    animal_list = f.read().split('\n')

with open("main/adjectives.txt", "r") as f:
    adjective_list = f.read().split('\n')



def create_user(request):
    if request.session.get('id') is None: # First Access
        request.session['id'] = str(uuid1.uuid1())
        try:
            user = User(session_id=request.session['id'],
                        nickname=random.choice(adjective_list)+" "+random.choice(animal_list)
                        )
            user.save()
            
        except Exception as e:
            return Message(Status.INTERNAL_ERROR, f'Internal server error, {e}')
        
        return Message(Status.SUCCESS, user=user)

    else:
        return Message(Status.BAD_REQUEST, 'User already exists')

def get_user(request):
    session_id = request.session.get('id')
    if session_id is None:
        return Message(Status.BAD_REQUEST, 'No session id.')
  
    try:
        user = User.objects.get(session_id=session_id)
    except User.DoesNotExist:
        return Message(Status.NOT_FOUND, 'No such user.')

    return Message(Status.SUCCESS, user=user)

def get_or_create_user(request):
    msg_user = get_user(request)
    if is_success(msg_user): user = msg_user.data['user']

    else:
        msg_user = create_user(request)
        if is_success(msg_user): user = msg_user.data['user']
        else: return msg_user
    
    return Message(Status.SUCCESS, user=user)
