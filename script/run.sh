python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
gunicorn everyboard_back.wsgi --bind 0.0.0.0:8000 