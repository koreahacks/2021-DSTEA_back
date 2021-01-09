import uuid1
from django.shortcuts import render
from django.http import HttpResponse

from main.models import Path
from main.utils.common import Message, Status


def make_board(request):
    return

def get_board(request, board_url):
    return

def file_upload(request, board_url):
    return

def write(request, board_url):
    try:
        path = Path(board=Board.objects.get(board_url=board_url),
                    page_id=request.GET['page_id'],
                    session_id=request.session['id'],
                    is_public=request.GET['public'],
                    pen_type=request.GET['pen_type'],
                    color=request.GET['color'],
                    data=request.GET['data']
                    )
        path.save()
        return Message(Status.SUCCESS, is_valid=True).res()
    except:
        return Message(Status.INTERNAL_ERROR, is_valid=False).res()