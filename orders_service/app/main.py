from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api_v1 import router as api_v1_router
from lifespan import lifespan
from metrics import metrics_middleware, metrics_endpoint

app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title='Order Service',
    description='Список оформленных заказов. FastAPI, PostgreSQL, SQLAlchemy(v2), Kafka, Docker',
)
app.include_router(api_v1_router)
app.middleware('http')(metrics_middleware)


@app.get('/metrics')
async def metrics():
    return metrics_endpoint()
