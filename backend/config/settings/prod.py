from .base import *
DEBUG = True
ALLOWED_HOSTS = ['Dancoder1.pythonanywhere.com', '*']
SECRET_KEY = 'prod-secret-key-xyz123'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
CORS_ALLOW_ALL_ORIGINS = True
