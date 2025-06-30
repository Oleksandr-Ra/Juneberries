from uuid import UUID

import httpx
from fastapi import HTTPException, status

from api_v1.orders.schemas import ProductDataSchema
from config import settings


async def fetch_product_data(product_id: UUID, token: str) -> ProductDataSchema:
    """Makes HTTP request to the product microservice to retrieve product data."""

    url = f'{settings.product_url}/{product_id}'
    headers = {'Authorization': f'Bearer {token}'}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=3.0)

            if response.status_code == status.HTTP_200_OK:
                return ProductDataSchema(**response.json())

            elif response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='The product with ID {product_id} is not found in the catalog.',
                )
            else:
                # Another errors from catalog service.
                response.raise_for_status()

        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='No connection with catalog service. Try again later.',
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Catalog service is temporarily unavailable. Try again later.',
            )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Unknown error when querying the catalog service.',
    )
