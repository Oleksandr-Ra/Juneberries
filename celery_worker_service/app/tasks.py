import random
import time
from datetime import timedelta

import requests

import redis_connect
from celery_app import celery
from config import settings
from logging_config import setup_logger

logger = setup_logger('celery_worker_service')


@celery.task(name='tasks.update_currency_rate')
def update_currency_rate() -> None:
    """Update and cache currency rate."""

    logger.info('Starting scheduled currency rate update...')

    if redis_connect.redis_client is None:
        logger.error('Cannot update rate from Redis, client not initialized.')
        return

    try:
        base_currency: str = settings.exchange_api.base_currency
        target_currency: str = settings.exchange_api.target_currency
        rate_key: str = f'rates:{base_currency}_{target_currency}'

        response: dict | None = fetch_currency_rate_from_api()
        if response is None:
            logger.error('Failed to fetch currency rate from API.')
            return

        rate: float = response['rates'][target_currency]
        logger.info(f'Fetched new rate from API: {rate_key} = {rate}')

        redis_connect.redis_client.set(
            name=rate_key,
            value=rate,
            ex=timedelta(minutes=settings.redis.rate_exp),
        )
        logger.info(f'Successfully updated and cached currency rate for: {rate_key}.')

    except Exception as e:
        logger.error(f'An error occurred during currency rate update: {e}', exc_info=True)


def fetch_currency_rate_from_api(retries: int = 4, base_delay: float = 1.0) -> dict | None:
    """Makes HTTP request to the external API to retrieve the rate, with retry logic."""

    url = settings.exchange_api.url
    params = {
        'access_key': settings.exchange_api.key,
        'base': settings.exchange_api.base_currency,
        'symbols': settings.exchange_api.available_currency,
    }

    for attempt in range(1, retries):
        try:
            response = requests.get(url=url, params=params, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f'Error from rate API (status={response.status_code}). Attempt {attempt}/{retries}.')

        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f'API connection error: {e}. Attempt {attempt}/{retries}.')
        except Exception as e:
            logger.error(f'Unexpected error: {e}. Attempt {attempt}/{retries}.')

        if attempt < retries:
            delay = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0, delay)
            logger.info(f'Waiting {jitter:.2f} seconds before next retry...')
            time.sleep(jitter)

    return None
