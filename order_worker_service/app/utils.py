import asyncio
import logging
import random
from datetime import timedelta

import aiohttp

import redis_connect
from config import settings

logger = logging.getLogger(__name__)


async def get_currency_rate(target_currency: str = 'RUB') -> float:
    """
    Retrieves currency rate. First it searches in Redis,
    if it doesn't find it, it accesses external API.
    """
    if redis_connect.redis_client is None:
        raise RuntimeError('Redis client not initialized')

    rate_key: str = f'rates:{settings.exchange_api.base_currency}_{target_currency}'
    # 1. Get from Redis
    cached_rate: str | None = await redis_connect.redis_client.get(rate_key)
    if cached_rate:
        logger.info(f'Found currency rate in cache: {cached_rate}')
        return float(cached_rate)

    # If not in Redis, get from external API
    logger.info('No rate in cache, fetching from external API.')

    response: dict | None = await fetch_currency_rate_from_api()
    if response is None:
        raise

    rate: float = response['rates'][target_currency]  # get rate from response
    logger.info(f'Fetched new rate from API: {rate_key} = {rate}')

    # Set in Redis with expiration
    await redis_connect.redis_client.set(
        name=rate_key,
        value=rate,
        ex=timedelta(minutes=settings.redis.rate_exp),
    )
    return rate


async def fetch_currency_rate_from_api(retries: int = 3, base_delay: float = 1.0) -> dict | None:
    """Makes HTTP request to the external API to retrieve the rate, with retry logic."""

    url = settings.exchange_api.url
    params = {
        'access_key': settings.exchange_api.key,
        'base': settings.exchange_api.base_currency,
        'symbols': settings.exchange_api.available_currency,
    }
    timeout = aiohttp.ClientTimeout(total=5.0)

    for attempt in range(1, retries):
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url=url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f'Error from rate API (status={response.status}). Attempt {attempt}/{retries}.')

            except (aiohttp.ClientConnectionError, aiohttp.ClientTimeout) as e:
                logger.error(f'API connection error: {e}. Attempt {attempt}/{retries}.')
            except Exception as e:
                logger.error(f'Unexpected error: {e}. Attempt {attempt}/{retries}.')

        if attempt < retries:
            delay = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0, delay)
            logger.info(f'Waiting {jitter:.2f} seconds before next retry...')
            await asyncio.sleep(jitter)

    return None
