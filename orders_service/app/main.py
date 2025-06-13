from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Order Service',
    description='Список оформленных заказов. FastAPI, PostgreSQL, SQLAlchemy(v2), Docker, Pytest',
)
