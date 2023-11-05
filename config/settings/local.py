from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [] # 로컬 환경에서만 runserver 시 python manage.py runserver --settings=config.settings.local 사용

DJANGO_APPS += [
    
]

PROJECT_APPS +=[

]

THIRD_PARTY_APPS += [

]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]