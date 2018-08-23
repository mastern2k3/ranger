FROM python:3.6-alpine

RUN pip3 install pipenv

RUN mkdir /app
RUN mkdir /monitored
RUN mkdir /archive

COPY . /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system

WORKDIR /app

CMD ["python", "main.py", "-t", "/monitored", "-a", "/archive"]
