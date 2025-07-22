import asyncio
import logging
import time

from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    name='http_requests_total', documentation='Total HTTP requests',
    labelnames=['method', 'endpoint', 'http_status'],
)
REQUEST_LATENCY = Histogram(
    name='latency_seconds', documentation='HTTP request latency',
    labelnames=['method', 'endpoint'],
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


async def metrics_middleware(request: Request, call_next):
    if request.url.path.startswith('/metrics'):
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)

    return response


def metrics_endpoint():
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
