#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd selstagram2

export DJANGO_SETTINGS_MODULE=settings.staging
celery -A selstagram2.celerybeat beat -l DEBUG
unset DJANGO_SETTINGS_MODULE

cd -