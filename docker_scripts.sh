#!/bin/bash

pipenv run python3 manage.py migrate
pipenv run python3 manage.py runserver 0:8000
pipenv run celery -A mysite worker -l info