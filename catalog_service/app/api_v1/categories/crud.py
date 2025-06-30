from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.categories.schemas import CategoryCreateSchema, CategoryUpdateSchema, CategoryUpdatePartialSchema
from models import Category


async def get_category(session: AsyncSession, category_id: UUID) -> Category | None:
    return await session.get(Category, category_id)


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.scalars(
        select(Category)
        .order_by(Category.name)
    )
    return list(result.all())


async def create_category(session: AsyncSession, data: CategoryCreateSchema) -> Category:
    category = Category(**data.model_dump())
    session.add(category)
    await session.commit()
    return category


async def update_category(
        session: AsyncSession,
        category: Category,
        category_data: CategoryUpdateSchema | CategoryUpdatePartialSchema,
        partial: bool = False,
) -> Category:
    for key, value in category_data.model_dump(exclude_unset=partial).items():
        setattr(category, key, value)
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.commit()
