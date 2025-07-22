from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI, Depends, Request
from fastapi.responses import ORJSONResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1 import router as api_v1_router
from db import get_db
from lifespan import lifespan
from logging_config import setup_logger

logger = setup_logger('orders_service')

app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Order Service',
    description='Список оформленных заказов. FastAPI, PostgreSQL, SQLAlchemy(v2), Kafka, Docker',
)
app.include_router(api_v1_router)


@app.get('/metrics', tags=['Metrics'])
async def metrics():
    pass


@app.get('/live', tags=['HealthCheck'])
def liveness_check():
    return {'status': 'alive'}


@app.get('/ready', tags=['HealthCheck'])
async def readiness_check(
        request: Request,
        session: AsyncSession = Depends(get_db),
):
    try:
        # DB
        await session.execute(text('SELECT 1'))

        # Kafka
        producer = getattr(request.app.state, 'producer', None)
        if not producer:
            raise RuntimeError('Kafka producer not initialized')

        consumer = getattr(request.app.state, 'consumer', None)
        if not consumer:
            raise RuntimeError('Kafka consumer not initialized')

        if not await check_kafka_producer(producer=producer):
            raise RuntimeError('Kafka producer unavailable')

        if not await check_kafka_consumer(consumer=consumer):
            raise RuntimeError('Kafka consumer unavailable')

        return {'status': 'ready'}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'not ready', 'reason': str(e)},
        )


async def check_kafka_producer(producer: AIOKafkaProducer) -> bool:
    try:
        topics = producer.client.cluster.topics()
        return bool(topics)
    except Exception as e:
        logger.error(f'Kafka Producer error: {e}', exc_info=True)
        return False


async def check_kafka_consumer(consumer: AIOKafkaConsumer) -> bool:
    try:
        topics = await consumer.topics()
        return bool(topics)
    except Exception as e:
        logger.error(f'Kafka Consumer error: {e}', exc_info=True)
        return False
