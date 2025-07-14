import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api_v1 import router as api_v1_router
from config import settings
from metrics import metrics_middleware, metrics_endpoint, RedisWithMetrics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_instance = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=True,
    )
    app.state.redis = RedisWithMetrics(redis_instance=redis_instance)
    logger.info('✅ Successfully connected to Redis.')

    yield

    await app.state.redis.close()
    logger.info('❌ Redis connection closed.')


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Catalog Service',
    description='Список товаров и категорий. FastAPI, PostgreSQL, SQLAlchemy(v2), Alembic, Redis, Kafka, Docker',
    version='1.0.0',
)
app.include_router(api_v1_router)
app.middleware('http')(metrics_middleware)


@app.get('/metrics')
def metrics():
    return metrics_endpoint()
