FROM python:3.9.2-alpine3.13

WORKDIR /code

RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libxml2-dev \
    libxslt-dev
#    libffi-dev \
#    make \
#    openrc \
#    openssh \
#    python3-dev \
#    postgresql-dev \
#    cargo

COPY ./requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

CMD python main.py
#CMD tail -f
