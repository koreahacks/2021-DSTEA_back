from main.models import Board, Path
from main.utils.common import Message, Status
from django.db.models import Q

def get_all_path(board_url, session_id):
    try:
        board = Board.objects.filter(board_url=board_url).get()
    except Board.DoesNotExist:
        return Message(Status.NOT_FOUND, 'No such board.')

    try:
        path_list = Path.objects.filter(
            Q(board=board) and 
            (Q(session_id=session_id) or Q(is_public=True))
        ).all()
    except Exception as e:
        return Message(Status.INTERNAL_ERROR, f"Internal server error, {e}")
    
    result = []
    for path in path_list:
        result.append({
            "id": path.id,
            "page_id": path.page_id,
            "session_id": path.session_id,
            "is_public": path.is_public,
            "color": path.color,
            "data": path.data,
            "pen_type": path.pen_type,
        })

    return Message(Status.SUCCESS, path_list=result)
