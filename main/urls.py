from django.urls import path
from main import views

app_name = "main"

urlpatterns = [
    path('', views.make_board, name="make_board"),
    path('api/<uuid:board_url>', views.get_board, name="get_board"),
    path('api/<uuid:board_url>/file_upload', views.file_upload, name="file_upload"),
    path('api/<uuid:board_url>/write', views.write, name='write')
]