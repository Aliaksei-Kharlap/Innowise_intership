#!/bin/bash

pipenv run alembic revision --autogenerate -m "Second"
pipenv run alembic upgrade head
pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8001

