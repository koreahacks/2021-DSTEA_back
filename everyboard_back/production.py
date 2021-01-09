from everyboard_back.base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
        'NAME': 'EveryBoardDB',
        'USER': 'everyboard_admin',
        'PASSWORD': os.getenv('DB_PASSWORD'),
    }
}