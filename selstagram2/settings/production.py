#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_ENV_DB', 'postgres'),
        'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', 'localhost'),
        'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', ''),
    },
}

DEBUG = False

ALLOWED_HOSTS = ['*']
