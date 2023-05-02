#!/bin/bash

pipenv run celery flower --broker=$CELERY_BROKER_URL --port=5555
