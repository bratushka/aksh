FROM python:3.9.2-alpine3.13

WORKDIR /code

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev
#    libffi-dev \
#    make \
#    linux-headers \
#    openrc \
#    openssh \
#    python3-dev \
#    cargo

COPY ./requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

CMD ./manage.py runserver 0.0.0.0:8000
