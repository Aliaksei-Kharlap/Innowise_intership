FROM ubuntu:latest

RUN apt-get update && apt-get update

RUN apt-get -y install python3-pip

RUN pip install --upgrade pip
RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile

COPY . ./

EXPOSE 8000

ENTRYPOINT pipenv run python3 manage.py runserver 127.0.0.1:8000
