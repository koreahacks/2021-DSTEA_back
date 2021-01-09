import uuid1
from django.shortcuts import render
from django.http import HttpResponse

from main.models import Path
from main.utils.common import Message, Status, is_success
from main.utils.file import ppt2pdf, pdf2jpgs, save_file
from main.utils.file import EXT_PPT, EXT_PDF


def make_board(request):
    return

def get_board(request, board_url):
    return

def file_upload(request, board_url):
    if request.method != 'POST':
        return Message(Status.FORBIDDEN, 'Method not allowed.')
    
    if request.FILES.get('file') is None:
        return Message(Status.BAD_REQUEST, 'Wrong form.')

    file = request.FILES['file']
    ext = file.name.split('.')[-1]

    saved_file = save_file(file, board_url)
    if ext in EXT_PPT:
        msg_pdf_file = ppt2pdf(saved_file)
        if is_success(msg_pdf_file): pdf_file = msg_pdf_file.data['filename']
        else: return msg_pdf_file.res()

    elif ext in EXT_PDF:
        pdf_file = saved_file
    
    else:
        return Message(Status.BAD_REQUEST, "Wrong file.").res()
    
    page_num = pdf2jpgs(pdf_file, board_url)

    return Message(Status.SUCCESS, page_num=page_num).res()

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