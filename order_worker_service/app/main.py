import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from redis.asyncio import Redis

import redis_connect
from config import settings
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

    delivery_price_target: float = round(delivery_price * rate, 2)
    cart_price_target: float = round(cart_price * rate, 2)
    total_price_target: float = cart_price_target + delivery_price_target

    update_message = {
        'event_type': 'ORDER_UPDATED',
        'order_id': order_id,
        'delivery_price': delivery_price_target,
        'cart_price': cart_price_target,
        'total_price': total_price_target,
        'status': 'updated',
    }

    await producer.send(topic=settings.kafka.order_topic, value=update_message)
    logger.info(f'ORDER_UPDATED event sent for order_id: {order_id}')


async def main() -> None:
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
    )
    try:
        # Create Redis connection and save it in our redis_connect module.
        redis_connect.redis_client = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            decode_responses=True,
        )
        await redis_connect.redis_client.ping()
        logger.info('Successfully connected to Redis.')

        await producer.start()
        await consumer.start()
        logger.info('Kafka Consumer and Producer started.')

        async for msg in consumer:
            if msg.value.get('event_type') == 'ORDER_CREATED':
                await process_message(message_data=msg.value, producer=producer)

    except Exception as e:
        logger.error(f'A critical error occurred: {e}', exc_info=True)

    finally:
        await consumer.stop()
        await producer.stop()
        logger.info('Kafka clients stopped.')

        if redis_connect.redis_client:
            await redis_connect.redis_client.aclose()
            logger.info('Redis connection closed.')
        logger.info('Shutdown complete.')


if __name__ == '__main__':
    asyncio.run(main())
