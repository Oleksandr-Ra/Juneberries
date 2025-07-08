import asyncio
import json
import logging
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI

from api_v1.orders.services import process_message
from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def consume_events():
    consumer = AIOKafkaConsumer(
        settings.kafka.order_topic,
        bootstrap_servers=[settings.kafka.broker],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
    )
    try:
        await consumer.start()
    except Exception as e:
        logger.error(f'🛑 Could not connect to AIOKafkaConsumer: {e}')

    try:
        async for msg in consumer:
            logger.info(f'📥 Received: {msg.value} | type: {type(msg.value)}')
            if msg.value.get('event_type') == 'ORDER_UPDATED':
                await process_message(message_data=msg.value)
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """START and STOP: AIOKafkaProducer, AIOKafkaConsumer"""
    producer = AIOKafkaProducer(
        bootstrap_servers=[settings.kafka.broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    try:
        await producer.start()
    except Exception as e:
        app.state.producer = None
        logger.error(f'🛑 Could not connect to AIOKafkaProducer: {e}')

    app.state.producer = producer
    logger.info('✅ Successfully connected to AIOKafkaProducer.')

    consumer_task = asyncio.create_task(consume_events())
    app.state.consumer_task = consumer_task
    logger.info('✅ Successfully connected to AIOKafkaConsumer.')

    yield

    if app.state.producer:
        await app.state.producer.flush()
        await app.state.producer.stop()
        logger.info('❌ AIOKafkaProducer closed')
    else:
        logger.info('❗ No active AIOKafkaProducer found in "app.state" to close.')

    app.state.consumer_task.cancel()
    try:
        await app.state.consumer_task
    except asyncio.CancelledError:
        logger.info('❌ Consumer task successfully canceled')
