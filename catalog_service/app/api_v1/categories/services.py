from uuid import UUID

from fastapi import Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import CategoryCreateSchema, CategoryUpdateSchema
from db import get_db
from models import Category


async def create_category(
        category_data: CategoryCreateSchema,
        session: AsyncSession = Depends(get_db),
) -> Category:
    return await crud.create_category(session=session, data=category_data)


async def get_categories(
        session: AsyncSession = Depends(get_db),
) -> list[Category]:
    return await crud.get_categories(session=session)


async def get_category_by_id(
        category_id: UUID = Path(...),
        session: AsyncSession = Depends(get_db),
) -> Category:
    category: Category | None = await crud.get_category(session=session, category_id=category_id)
    if category:
        return category
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Category {category_id} not found!',
    )


async def update_category(
        category_data: CategoryUpdateSchema,
        category: Category = Depends(get_category_by_id),
        session: AsyncSession = Depends(get_db),
) -> Category:
    return await crud.update_category(session=session, category=category, category_data=category_data)


async def delete_category(
        category: Category = Depends(get_category_by_id),
        session: AsyncSession = Depends(get_db),
) -> None:
    await crud.delete_category(session=session, category=category)
