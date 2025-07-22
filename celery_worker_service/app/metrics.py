from prometheus_client import Counter, start_http_server

REDIS_OPS = Counter(
    name='redis_ops', documentation='Total Redis operations',
    labelnames=['operation', 'status'],
)


class RedisWithMetrics:
    def __init__(self, redis_instance):
        self.client = redis_instance

    def __getattr__(self, name):
        orig = getattr(self.client, name)

        def wrapper(*args, **kwargs):
            try:
                result = orig(*args, **kwargs)
                REDIS_OPS.labels(operation=name, status='success').inc()
                return result
            except Exception:
                REDIS_OPS.labels(operation=name, status='fail').inc()
                raise

        return wrapper

    async def close(self):
        await self.client.close()


start_http_server(8000)