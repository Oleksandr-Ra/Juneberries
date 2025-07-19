from celery import Celery
from celery.schedules import crontab

from config import settings
from logging_config import setup_logger

logger = setup_logger('celery_worker_service')

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
