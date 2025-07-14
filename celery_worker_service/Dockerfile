FROM python:3.12-slim

RUN groupadd -g 1001 celery_worker && useradd -u 1001 -g celery_worker api

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

USER api
