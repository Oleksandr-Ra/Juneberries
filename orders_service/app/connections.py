from aiokafka import AIOKafkaProducer
from fastapi import Request


async def get_producer(request: Request) -> AIOKafkaProducer:
    """
    FastAPI dependency to get AIOKafkaProducer from "app.state".
    """
    producer = getattr(request.app.state, 'producer', None)
    if producer is None:
        raise RuntimeError('AIOKafkaProducer is not initialized')
    return producer
