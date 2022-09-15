FROM python:3.10

WORKDIR /app

COPY . /app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev


RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv shell
RUN pipenv install --dev


CMD ["python", "index.py"]