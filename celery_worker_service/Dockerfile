FROM python:3.12-slim

RUN groupadd -g 1001 worker && useradd -u 1001 -g worker api

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

USER api

CMD ["python", "main.py"]