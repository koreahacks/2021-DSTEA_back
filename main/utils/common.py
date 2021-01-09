import json
from django.http import JsonResponse

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
