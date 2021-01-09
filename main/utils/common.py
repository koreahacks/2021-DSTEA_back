import json
from django.http import JsonResponse, HttpResponse
from django.template import Template, RequestContext

class Status():
    SUCCESS = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class Message():
    def __init__(self, status: int, msg: str=None, **kwargs):
        self.data = {'status': status}
        if msg:
            self.data.update({'msg': msg})
        for key in kwargs.keys():
            self.data.update({key: kwargs[key]})

    def dump(self, **kwargs):
        return json.dumps(self.data, **kwargs)

    def res(self):
        return JsonResponse(self.data)

    def __str__(self):
        return json.dumps(self.data)


def is_success(msg: Message):
    if msg.data['status'] is Status.SUCCESS:
        return True
    else:
        return False


def send_csrf(request):
    return HttpResponse(Template('{% csrf_token %}').render(RequestContext(request)))