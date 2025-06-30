from uuid import UUID

from api_v1.products.schemas import ProductCreateSchema, ProductUpdateSchema, ProductUpdatePartialSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Product


async def get_product(session: AsyncSession, product_id: UUID) -> Product | None:
    return await session.get(Product, product_id)


async def get_products(session: AsyncSession) -> list[Product]:
    result = await session.scalars(
        select(Product)
        .options(
            selectinload(Product.category)
        )
        .order_by(Product.created_at.desc())
    )
    return list(result.all())


async def create_product(session: AsyncSession, data: ProductCreateSchema) -> Product:
    product = Product(**data.model_dump())
    session.add(product)
    await session.commit()
    return product


async def update_product(
        session: AsyncSession,
        product: Product,
        product_data: ProductUpdateSchema | ProductUpdatePartialSchema,
        partial: bool = False,
) -> Product:
    for key, value in product_data.model_dump(exclude_unset=partial).items():
        setattr(product, key, value)
    await session.commit()
    return product


async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()
