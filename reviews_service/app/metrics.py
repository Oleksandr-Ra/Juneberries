import time

from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    name='http_requests_total',
    documentation='Total HTTP requests',
    labelnames=['method', 'endpoint', 'http_status'],
)

REQUEST_LATENCY = Histogram(
    name='latency_seconds',
    documentation='HTTP request latency',
    labelnames=['method', 'endpoint'],
)


async def metrics_middleware(request: Request, call_next):
    if request.url.path.startswith('/metrics'):
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)

    return response


def metrics_endpoint():
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
