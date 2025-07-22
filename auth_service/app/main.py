from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1 import router as api_v1_router
from db import get_db
from logging_config import setup_logger
from metrics import metrics_middleware, metrics_endpoint

logger = setup_logger('auth_service')


app = FastAPI(
    default_response_class=ORJSONResponse,
    title='Auth Service',
    description='Выдача/обновление access и refresh токенов. FastAPI, PostgreSQL, JWT, Redis (для refresh токенов), '
                'SQLAlchemy(v2), Docker, Pytest',
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
async def readiness_check(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text('SELECT 1'))
        return {'status': 'ready'}
    except Exception as e:
        return JSONResponse(status_code=500, content={'status': 'not ready', 'reason': str(e)})

