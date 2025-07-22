import asyncio
import json
import logging
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI

from api_v1.orders.services import process_message
from config import settings

logger = logging.getLogger(__name__)


async def consume_events(consumer: AIOKafkaConsumer):
    try:
        async for msg in consumer:
            await process_message(message_data=msg.value)
            await consumer.commit()
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """START and STOP: AIOKafkaProducer, AIOKafkaConsumer"""
    # --- PRODUCER ---
    producer = AIOKafkaProducer(
        bootstrap_servers=[settings.kafka.broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    try:
        await producer.start()
        app.state.producer = producer
        logger.info('Successfully connected to AIOKafkaProducer.')
    except Exception as e:
        app.state.producer = None
        logger.error(f'Could not connect to AIOKafkaProducer: {e}')

    # --- CONSUMER ---
    consumer = AIOKafkaConsumer(
        settings.kafka.order_update_topic,
        bootstrap_servers=[settings.kafka.broker],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='orders_service_group'
    )
    try:
        await consumer.start()
        app.state.consumer = consumer
        logger.info('Successfully connected to AIOKafkaConsumer.')
    except Exception as e:
        app.state.consumer = None
        logger.error(f'Could not connect to AIOKafkaConsumer: {e}')

    # --- START CONSUMER TASK ---
    consumer = getattr(app.state, 'consumer', None)
    if consumer:
        consumer_task = asyncio.create_task(consume_events(consumer=consumer))
        app.state.consumer_task = consumer_task

    yield

    # --- SHUTDOWN PRODUCER ---
    producer = getattr(app.state, 'producer', None)
    if producer:
        await producer.flush()
        await producer.stop()
        logger.info('AIOKafkaProducer closed')
    else:
        logger.info('No active AIOKafkaProducer found in "app.state" to close.')

    # --- SHUTDOWN CONSUMER ---
    consumer = getattr(app.state, 'consumer', None)
    if consumer:
        await consumer.stop()
        logger.info('AIOKafkaConsumer closed')
    else:
        logger.info('No active AIOKafkaConsumer found in "app.state" to close.')

    # --- CANCEL CONSUMER TASK ---
    consumer_task = getattr(app.state, 'consumer_task', None)
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info('Consumer task successfully canceled')
    else:
        logger.info('No active consumer task found in "app.state" to cancel.')
