from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Catalog Service',
    description='Список товаров и категорий. FastAPI, PostgreSQL, SQLAlchemy(v2), Docker, Pytest',
)
