from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api_v1 import router as api_v1_router


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Catalog Service',
    description='Список товаров и категорий. FastAPI, PostgreSQL, SQLAlchemy(v2), Alembic, Redis, Kafka, Docker',
    version='1.0.0',
)
app.include_router(api_v1_router)
