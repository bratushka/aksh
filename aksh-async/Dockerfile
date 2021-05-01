FROM python:3.9.2-alpine3.13

WORKDIR /code

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    make \
    libffi-dev \
    # lxml dependencies
    libxml2-dev \
    libxslt-dev \
    # textract dependencies
    jpeg-dev \
    libjpeg \
    antiword \
    poppler-utils \
    tesseract-ocr

# textract dependencies
ENV TESSDATA_PREFIX /tesseract-ocr
RUN mkdir $TESSDATA_PREFIX
RUN wget --directory-prefix=$TESSDATA_PREFIX https://github.com/tesseract-ocr/tessdata/raw/master/ukr.traineddata

# Application
COPY ./requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

CMD uvicorn app.main:app \
    --reload \
    --host=0.0.0.0 \
    --port=8001 \
    --no-access-log
