from redis import Redis

from config import settings
from metrics import RedisWithMetrics

redis_instance = Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.db,
    decode_responses=True,
)
redis_client = RedisWithMetrics(redis_instance=redis_instance)
