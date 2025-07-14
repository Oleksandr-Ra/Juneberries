from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api_v1 import router as api_v1_router
from metrics import metrics_middleware, metrics_endpoint


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Auth Service',
    description='Выдача/обновление access и refresh токенов. FastAPI, PostgreSQL, JWT, Redis (для refresh токенов), '
                'SQLAlchemy(v2), Docker, Pytest',
    version='1.0.0',
)
app.include_router(api_v1_router)
app.middleware('http')(metrics_middleware)


@app.get('/metrics')
def metrics():
    return metrics_endpoint()
