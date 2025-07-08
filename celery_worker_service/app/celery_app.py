from celery import Celery

from config import settings

celery = Celery(
    main='app',
    broker=settings.redis.redis_url,
    backend=settings.redis.redis_url,
    include=['app.tasks']
)

celery.conf.update(
    task_track_started=True,
)
