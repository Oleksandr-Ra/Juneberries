import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api_v1 import router as api_v1_router
from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    client = AsyncIOMotorClient(settings.db.url)
    app_.state.mongo_client = client
    app_.state.db = client[settings.db.reviews_mongo_db]
    logger.info('Connected to MongoDB')

    yield

    client.close()
    logger.info('MongoDB connection closed')


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Reviews Service',
    description='Сохранение и редактирование отзывов по товарам. FastAPI, MongoDB, Kafka, Docker',
)
app.include_router(api_v1_router)


@app.get('/metrics')
async def metrics():
    pass
