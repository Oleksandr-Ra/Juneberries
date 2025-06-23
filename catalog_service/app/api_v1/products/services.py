from uuid import UUID

from fastapi import Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import Product
from . import crud
from .schemas import ProductCreateSchema, ProductUpdatePartialSchema


async def create_product(
        product_data: ProductCreateSchema,
        session: AsyncSession = Depends(get_db),
) -> Product:
    return await crud.create_product(session=session, data=product_data)


async def get_products(
        session: AsyncSession = Depends(get_db),
) -> list[Product]:
    return await crud.get_products(session=session)


async def get_product_by_id(
        product_id: UUID = Path,
        session: AsyncSession = Depends(get_db),
) -> Product:
    product: Product | None = await crud.get_product(session=session, product_id=product_id)
    if product:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Product {product_id} not found!',
    )


async def update_product(
        product_data: ProductUpdatePartialSchema,
        product: Product = Depends(get_product_by_id),
        session: AsyncSession = Depends(get_db),
) -> Product:
    return await crud.update_product(session=session, product=product, product_data=product_data, partial=True)


async def delete_product(
        product: Product = Depends(get_product_by_id),
        session: AsyncSession = Depends(get_db),
) -> None:
    await crud.delete_product(session=session, product=product)
