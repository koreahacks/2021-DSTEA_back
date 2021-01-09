import uuid1
from django.http import HttpResponse

from main.models import User, Board, Path
from main.utils.common import Message, Status, is_success
from main.utils.common import send_csrf
from main.utils.file import ppt2pdf, pdf2jpgs
from main.utils.file import save_file, get_images
from main.utils.file import EXT_PPT, EXT_PDF
from main.utils.user import create_user, get_or_create_user
from main.utils.path import get_all_path

def make_board(request):
    msg_user = create_user(request)
    if msg_user.data['status'] == Status.BAD_REQUEST: # Redirect user's board url
        try:
            user = User.objects.get(session_id=request.session.get('id'))
            return Message(Status.SUCCESS, board=user.board.board_url).res()
        except Exception as e:
            return Message(Status.INTERNAL_ERROR, f'Internal server error, {e}').res()

    elif is_success(msg_user): # make new board and give to user
        try:
            user = msg_user.data['user']
            board = Board(board_url=str(uuid1.uuid1()),
                        admin_id=user.session_id
                        )
            board.save()
            user.board = board
            user.auth_write = True
            user.save()
            return Message(Status.SUCCESS, board=board.board_url).res()
        except Exception as e:
            return Message(Status.INTERNAL_ERROR, f'Internal server error, {e}', is_valid=False).res()

    else: # Internal Error in create_user func.
        return msg_user.res()

def get_board(request, board_url):
    msg_user = get_or_create_user(request)
    if is_success(msg_user): user = msg_user.data['user']
    else: return msg_user.res()

    try:
        
        board = Board.objects.filter(board_url=board_url).get()
    except Board.DoesNotExist:
        return Message(Status.NOT_FOUND, 'No such board.').res()
    
    msg_path_list = get_all_path(board_url, user.session_id)
    if is_success(msg_path_list): path_list = msg_path_list.data['path_list']
    else: return msg_path_list.res()

    return Message(Status.SUCCESS,
        user=user.session_id,
        nickname=user.nickname,
        is_auth=user.auth_write,
        path=path_list,
        page=get_images(board_url)
    ).res()

def file_upload(request, board_url):
    if request.method == 'GET':
        return send_csrf(request)
    if request.method != 'POST':
        return Message(Status.FORBIDDEN, 'Method not allowed.').res()
    
    if request.FILES.get('file') is None:
        return Message(Status.BAD_REQUEST, 'Wrong form.').res()

    file = request.FILES['file']
    ext = file.name.split('.')[-1]

    saved_file = save_file(file, board_url)
    if ext in EXT_PPT:
        msg_pdf_file = ppt2pdf(board_url)
        if is_success(msg_pdf_file): pdf_file = msg_pdf_file.data['filename']
        else: return msg_pdf_file.res()

    elif ext in EXT_PDF:
        pdf_file = saved_file
    
    else:
        return Message(Status.BAD_REQUEST, "Wrong file.").res()
    
    pdf2jpgs(pdf_file, board_url)

    return Message(Status.SUCCESS, pages=get_images(board_url)).res()

def write(request, board_url):
    if request.method != 'POST':
        return Message(Status.FORBIDDEN, 'Method not allowed.')
    try:
        path = Path(board=Board.objects.get(board_url=board_url),
                    page_id=request.POST['page_id'],
                    session_id=request.session['id'],
                    is_public=request.POST['public'],
                    pen_type=request.POST['pen_type'],
                    color=request.POST['color'],
                    data=request.POST['data']
                    )
        path.save()
        return Message(Status.SUCCESS, is_valid=True).res()
    except:
        return Message(Status.INTERNAL_ERROR, is_valid=False).res()

def userlist(request, board_url):
    try:
        users = User.objects.filter(board__board_url=str(board_url)).all()
        board = Board.objects.get(board_url=str(board_url))
        nicknames = []
        for user in users:
            if board.admin_id == user.session_id:
                auth = 0
            elif user.auth_write == True:
                auth = 1
            else:
                auth = 2
            nicknames.append({'nickname': user.nickname, 'auth': auth})
        return Message(Status.SUCCESS, user_info=nicknames).res()
    except:
        return Message(Status.INTERNAL_ERROR, is_valid=False).res()