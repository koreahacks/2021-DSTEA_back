from django.db import models
from colorfield.fields import ColorField

class Board(models.Model):
    board_url = models.CharField(max_length=40)
    admin_id = models.CharField(max_length=40, null=True)

class Path(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    page_id = models.IntegerField()
    session_id = models.CharField(max_length=40)
    is_public = models.BooleanField(default=False)
    pen_type = models.IntegerField(
        choices = [(0, 'pencil'),(1, 'pen'),(2, 'highlight')],
        default = 0
    )
    color = ColorField(default="#000000")
    data = models.TextField()

class User(models.Model):
    session_id = models.CharField(max_length=40)
    nickname = models.CharField(max_length=10)
    board = models.ForeignKey(Board, null=True, on_delete=models.CASCADE)
    auth_write = models.BooleanField(default=True)