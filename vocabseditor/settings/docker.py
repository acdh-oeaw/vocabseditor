import os
from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY', '1234verysecret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', True)
REDMINE_ID = os.environ.get('REDMINE_ID', 'vocabseditor')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'vocabseditor')


BASE_URL = f"https://{PROJECT_NAME}.acdh.oeaw.ac.at"

allowed_host = f"{PROJECT_NAME}.sisyphos.arz.oeaw.ac.at"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "0.0.0.0",
    allowed_host,
]


DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_TYP', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', '172.17.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432')
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


VOCABS_SETTINGS = {
    'default_prefix': VOCABS_DEFAULT_PEFIX,
    'default_ns': "http://www.vocabs/{}/".format(VOCABS_DEFAULT_PEFIX),
    'default_lang': "en"
}