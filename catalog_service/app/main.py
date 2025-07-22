from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.responses import ORJSONResponse, JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1 import router as api_v1_router
from db import get_db
from logging_config import setup_logger
from config import settings
from metrics import metrics_middleware, metrics_endpoint, RedisWithMetrics

logger = setup_logger('catalog_service')


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_instance = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=False,
    )
    try:
        app.state.redis = RedisWithMetrics(redis_instance=redis_instance)
        logger.info('Successfully connected to Redis.')
    except Exception as e:
        logger.error(f'Failed to connect to Redis: {e}')

    yield

    if app.state.redis:
        await app.state.redis.aclose()
        logger.info('Redis connection closed.')
    logger.info('Shutdown complete.')


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Catalog Service',
    description='Список товаров и категорий. FastAPI, PostgreSQL, SQLAlchemy(v2), Alembic, Redis, Kafka, Docker',
    version='1.0.0',
)
app.include_router(api_v1_router)
app.middleware('http')(metrics_middleware)


@app.get('/metrics', tags=['Metrics'])
def metrics():
    return metrics_endpoint()


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
        # Redis
        await request.app.state.redis.ping()

        return {'status': 'ready'}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'not ready', 'reason': str(e)},
        )
