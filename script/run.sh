python3 manage.py makemigrations
python3 manage.py migrate
gunicorn everyboard_back.wsgi --bind 0.0.0.0:8000 