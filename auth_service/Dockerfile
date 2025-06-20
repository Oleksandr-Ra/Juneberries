FROM python:3.12-slim

RUN groupadd -g 1001 auth && useradd -u 1001 -g auth api

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

USER api

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1