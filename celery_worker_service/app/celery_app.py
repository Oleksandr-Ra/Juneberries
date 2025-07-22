from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

from config import settings
from logging_config import setup_logger


@setup_logging.connect()
def configure_logging(**kwargs):
    setup_logger(service_name='celery_worker_service')


celery = Celery(
    main='app',
    broker=settings.redis.redis_url,
    backend=settings.redis.redis_url,
    include=['tasks']
)

celery.conf.beat_schedule = {
    'update-currency-rate-every-hour': {
        'task': 'tasks.update_currency_rate',
        'schedule': crontab(minute=0, hour='*'),
    }
}

celery.conf.timezone = 'UTC'
