from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import Request, HTTPException, status


async def get_producer(request: Request) -> AIOKafkaProducer:
    """
    FastAPI dependency to get AIOKafkaProducer from "app.state".
    """
    producer = getattr(request.app.state, 'producer', None)
    if not producer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='AIOKafkaProducer not available'
        )
    return producer
