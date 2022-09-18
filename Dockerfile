FROM python:3.10

RUN pip install --upgrade pip
RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile


COPY . ./

EXPOSE 8000

ENTRYPOINT ["./docker_scripts.sh"]