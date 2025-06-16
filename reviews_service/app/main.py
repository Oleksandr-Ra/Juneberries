from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from api_v1 import router as api_v1_router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.db.reviews_mongo_url)
    app.state.mongo_client = client
    app.state.db = client[settings.db.reviews_mongo_db]
    print("✅ Connected to MongoDB")

    yield

    client.close()
    print("🛑 MongoDB connection closed")


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Reviews Service',
    description='Сервис, где пользователь может оставить отзыв. FastAPI, MongoDB, Docker, Pytest',
)
app.include_router(api_v1_router)
