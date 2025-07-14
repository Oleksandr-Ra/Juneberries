from uuid import UUID

import aiohttp
from fastapi import HTTPException, status

from api_v1.orders.schemas import ProductDataSchema
from config import settings


async def fetch_product_data(product_id: UUID, token: str) -> ProductDataSchema:
    """Makes HTTP request to the product microservice to retrieve product data."""

    url = f'{settings.product_url}/{product_id}'
    headers = {'Authorization': f'Bearer {token}'}
    timeout = aiohttp.ClientTimeout(total=3.0)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url=url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return ProductDataSchema(**data)
                elif response.status == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='The product with ID {product_id} is not found in the catalog.',
                    )
                else:
                    text = await response.text()
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f'Catalog service error: {response.status} - {text}',
                    )

        except aiohttp.ClientConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='No connection with catalog service. Try again later.',
            )
        except aiohttp.ClientTimeout:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Catalog service is temporarily unavailable. Try again later.',
            )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Unknown error when querying the catalog service.',
    )
