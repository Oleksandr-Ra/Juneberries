import asyncio
import logging

from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

REDIS_OPS = Counter(
    name='redis_ops',
    documentation='Total Redis operations',
    labelnames=['operation', 'status'],
)
KAFKA_LAG = Gauge(
    name='kafka_consumer_lag',
    documentation='Kafka consumer lag',
    labelnames=['topic', 'partition'],
)


class RedisWithMetrics:
    def __init__(self, redis_instance):
        self.client = redis_instance

    def __getattr__(self, name):
        orig = getattr(self.client, name)

        async def wrapper(*args, **kwargs):
            try:
                result = await orig(*args, **kwargs)
                REDIS_OPS.labels(operation=name, status='success').inc()
                return result
            except Exception:
                REDIS_OPS.labels(operation=name, status='fail').inc()
                raise

        return wrapper

    async def close(self):
        await self.client.aclose()


async def calculate_lag(consumer):
    partitions = consumer.assignment()
    if not partitions:
        logging.info('---KAFKA---: No partitions assigned yet')
        return
    for tp in partitions:
        end_offsets = await consumer.end_offsets([tp])
        end_offset = end_offsets.get(tp, 0)
        if end_offset is None:
            continue

        committed = await consumer.committed(tp)
        if committed is None:
            committed = 0

        partition_lag = end_offset - committed
        KAFKA_LAG.labels(topic=tp.topic, partition=tp.partition).set(partition_lag)


async def lag_watcher(consumer):
    while True:
        try:
            await calculate_lag(consumer)
        except Exception as e:
            logger.error(f'LAG WATCHER FAILED: {e}', exc_info=True)
        await asyncio.sleep(10)
        logger.info('---LAG_WATCHER---')
