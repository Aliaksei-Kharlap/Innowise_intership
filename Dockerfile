FROM python:3.10

RUN pip install --upgrade pip && pip install pipenv
#RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile


COPY . ./

ENTRYPOINT ["./docker_scripts.sh"]