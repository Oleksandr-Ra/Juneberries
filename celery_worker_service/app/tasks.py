import asyncio
import logging
from datetime import timedelta

import aiohttp

import redis_connect
from celery_app import celery
from config import settings

logger = logging.getLogger(__name__)


@celery.task(name='tasks.update_currency_rate')
def update_currency_rate_task() -> None:
    """Sync Celery task that runs the async currency update."""
    asyncio.run(update_currency_rate())


async def update_currency_rate() -> None:
    """Update and cache currency rate."""

    logger.info('Starting scheduled currency rate update...')

    if redis_connect.redis_client is None:
        logger.error('❌ Cannot update rate: Redis client not initialized.')
        return

    try:
        base_currency: str = settings.exchange_api.base_currency
        target_currency: str = settings.exchange_api.target_currency
        rate_key: str = f'rates:{base_currency}_{target_currency}'

        response: dict | None = await fetch_currency_rate_from_api()
        if response is None:
            logger.error('🛑 Failed to fetch currency rate from API.')
            return

        rate: float = response['rates'][target_currency]
        logger.info(f'🆕 Fetched new rate from API: {rate_key} = {rate}')

        await redis_connect.redis_client.set(
            name=rate_key,
            value=rate,
            ex=timedelta(minutes=settings.redis.rate_exp),
        )
        logger.info(f'✅ Successfully updated and cached currency rate for {rate_key}.')

    except Exception as e:
        logger.error(f'An error occurred during currency rate update: {e}', exc_info=True)


async def fetch_currency_rate_from_api() -> dict | None:
    """Makes HTTP request to the external API to retrieve the rate."""

    url = settings.exchange_api.url
    params = {
        'access_key': settings.exchange_api.key,
        'base': settings.exchange_api.base_currency,
        'symbols': settings.exchange_api.available_currency,
    }
    timeout = aiohttp.ClientTimeout(total=5.0)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url=url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f'❌ Error to get data from rate API.')
                    return None

        except aiohttp.ClientConnectionError:
            logger.error(f'❌ No connection with catalog service. Try again later.')
            return None
        except aiohttp.ClientTimeout:
            logger.error(f'❌ Rate API is temporarily unavailable. Try again later.')
            return None
