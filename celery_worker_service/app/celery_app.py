from celery import Celery
from celery.schedules import crontab

from config import settings

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
