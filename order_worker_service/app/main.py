import asyncio
import json
import logging
from decimal import Decimal, ROUND_HALF_UP

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from prometheus_client import start_http_server
from redis.asyncio import Redis

import redis_connect
from config import settings
from metrics import RedisWithMetrics, lag_watcher
from utils import get_currency_rate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def process_message(message_data: dict, producer: AIOKafkaProducer) -> None:
    order_id: str | None = message_data.get('order_id')
    if order_id is None:
        return None

    delivery_price: float = message_data.get('delivery_price', 0.0)
    cart_price: float = message_data.get('cart_price', 0.0)

    logger.info(f'Starting processing for order_id: {order_id}')
    rate: float = await get_currency_rate(target_currency=settings.exchange_api.target_currency)

    delivery_price: Decimal = Decimal(str(delivery_price))
    cart_price: Decimal = Decimal(str(cart_price))
    rate: Decimal = Decimal(str(rate))

    delivery_price_target: Decimal = (delivery_price * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    cart_price_target: Decimal = (cart_price * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_price_target: Decimal = cart_price_target + delivery_price_target

    update_message = {
        'event_type': 'ORDER_UPDATED',
        'order_id': order_id,
        'delivery_price': float(delivery_price_target),
        'cart_price': float(cart_price_target),
        'total_price': float(total_price_target),
        'status': 'updated',
    }

    await producer.send(topic=settings.kafka.order_topic, value=update_message)
    logger.info(f'ORDER_UPDATED event sent (order_id: {order_id})')


async def main() -> None:
    lag_task = None
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka.broker,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=10000,
    )
    consumer = AIOKafkaConsumer(
        settings.kafka.order_topic,
        bootstrap_servers=settings.kafka.broker,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='order_worker_group',
    )
    try:
        # Create Redis connection and save it in our redis_connect module.
        redis_instance = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            decode_responses=True,
        )
        redis_connect.redis_client = RedisWithMetrics(redis_instance=redis_instance)
        try:
            await redis_connect.redis_client.ping()
            logger.info('Successfully connected to Redis.')
        except Exception as e:
            logger.error(f'Failed to connect to Redis: {e}')

        await producer.start()
        await consumer.start()
        logger.info('Kafka Consumer and Producer started.')

        lag_task = asyncio.create_task(lag_watcher(consumer))

        async for msg in consumer:
            if msg.value.get('event_type') == 'ORDER_CREATED':
                await process_message(message_data=msg.value, producer=producer)
                await consumer.commit()

    except Exception as e:
        logger.error(f'A critical error occurred: {e}', exc_info=True)

    finally:
        if lag_task:
            lag_task.cancel()
            try:
                await lag_task
            except asyncio.CancelledError:
                logger.info('Lag watcher task cancelled.')

        await consumer.stop()
        await producer.stop()
        logger.info('Kafka clients stopped.')

        if redis_connect.redis_client:
            await redis_connect.redis_client.aclose()
            logger.info('Redis connection closed.')

        logger.info('Shutdown complete.')


if __name__ == '__main__':
    start_http_server(8000)
    asyncio.run(main())
