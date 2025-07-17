import asyncio
import logging
import time

from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

REDIS_OPS = Counter(
    name='redis_ops', documentation='Total Redis operations',
    labelnames=['operation', 'status'],
)
KAFKA_LAG = Gauge(
    name='kafka_consumer_lag', documentation='Kafka consumer lag',
    labelnames=['topic', 'partition'],
)
KAFKA_END_OFFSET = Gauge(
    name='kafka_partition_end_offset', documentation='Kafka partition end offset',
    labelnames=['topic', 'partition'],
)
KAFKA_COMMITTED_OFFSET = Gauge(
    name='kafka_committed_offset', documentation='Kafka committed offset by consumer',
    labelnames=['topic', 'partition'],
)
KAFKA_LAG_TIMESTAMP = Gauge(
    name='kafka_lag_timestamp', documentation='Timestamp of last Kafka lag measurement (Unix time)',
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
        logging.info('KAFKA: No partitions assigned yet')
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
        topic = tp.topic
        partition = str(tp.partition)

        KAFKA_LAG.labels(topic=tp.topic, partition=tp.partition).set(partition_lag)
        KAFKA_END_OFFSET.labels(topic=topic, partition=partition).set(end_offset)
        KAFKA_COMMITTED_OFFSET.labels(topic=topic, partition=partition).set(committed)
        KAFKA_LAG_TIMESTAMP.labels(topic=topic, partition=partition).set(time.time())


async def lag_watcher(consumer):
    while True:
        try:
            await calculate_lag(consumer)
        except Exception as e:
            logger.error(f'LAG WATCHER FAILED: {e}', exc_info=True)
        await asyncio.sleep(10)
