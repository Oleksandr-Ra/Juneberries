from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api_v1 import router as api_v1_router
from config import settings
from logging_config import setup_logger

logger = setup_logger('reviews_service')


@asynccontextmanager
async def lifespan(app_: FastAPI):
    client = AsyncIOMotorClient(settings.db.url)
    app_.state.mongo_client = client
    app_.state.db = client[settings.db.reviews_mongo_db]
    logger.info('Connected to MongoDB')

    yield

    if app_.state.mongo_client:
        app_.state.mongo_client.close()
        logger.info('MongoDB connection closed')


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Reviews Service',
    description='Сохранение и редактирование отзывов по товарам. FastAPI, MongoDB, Kafka, Docker',
)
app.include_router(api_v1_router)


@app.get('/metrics', tags=['Metrics'])
async def metrics():
    pass


@app.get('/live', tags=['HealthCheck'])
def liveness_check():
    return {'status': 'alive'}


@app.get('/ready', tags=['HealthCheck'])
async def readiness_check(request: Request):
    try:
        mongo_client: AsyncIOMotorClient = request.app.state.mongo_client
        await mongo_client.admin.command('ping')

        return {'status': 'ready'}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'not ready', 'reason': str(e)},
        )
