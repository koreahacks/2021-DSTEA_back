python3 manage.py makemigrations
python3 manage.py migrate
uvicorn everyboard_back.asgi:application --port 8000 --workers 4