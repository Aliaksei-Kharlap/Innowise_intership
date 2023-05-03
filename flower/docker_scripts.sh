#!/bin/bash

pipenv run celery --broker=$CELERY_BROKER_URL flower --port=5555
