from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api_v1 import router as api_v1_router


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Order Service',
    description='Список оформленных заказов. FastAPI, PostgreSQL, SQLAlchemy(v2), Kafka, Docker',
)
app.include_router(api_v1_router)
