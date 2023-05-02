#!/bin/bash

pipenv run python3 manage.py migrate

#if [ "$DJANGO_SUPERUSER_USERNAME" ]
#then
#    pipenv run python manage.py createsuperuser \
#        --noinput \
#        --username $DJANGO_SUPERUSER_USERNAME \
#        --email $DJANGO_SUPERUSER_EMAIL \
#        --password $DJANGO_SUPERUSER_PASSWORD
#
#fi

pipenv run python3 manage.py runserver 0:8000
pipenv run celery -A mysite worker -l info
