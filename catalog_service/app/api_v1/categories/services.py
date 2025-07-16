import logging
import pickle
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, Request, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db import get_db
from models import Category
from . import crud
from .schemas import CategoryCreateSchema, CategoryUpdateSchema

logger = logging.getLogger(__name__)

CATEGORIES_KEY = 'categories:all'


async def create_category(
        request: Request,
        category_data: CategoryCreateSchema,
        session: AsyncSession = Depends(get_db),
) -> Category:
    category = await crud.create_category(session=session, data=category_data)
    await request.app.state.redis.delete(CATEGORIES_KEY)
    return category


async def get_categories(
        request: Request,
        session: AsyncSession = Depends(get_db),
) -> list[Category]:
    cached_categories = await request.app.state.redis.get(CATEGORIES_KEY)
    if cached_categories is not None:
        categories = pickle.loads(cached_categories)
        logger.info('Categories taken from Redis.')
        return categories

    categories = await crud.get_categories(session=session)
    logger.info('Categories taken from Postgres.')
    await request.app.state.redis.set(
        name=CATEGORIES_KEY,
        value=pickle.dumps(categories),
        ex=timedelta(days=settings.redis.categories_ttl),
    )
    logger.info('Categories are installed in Redis.')
    return categories


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
        request: Request,
        category_data: CategoryUpdateSchema,
        category: Category = Depends(get_category_by_id),
        session: AsyncSession = Depends(get_db),
) -> Category:
    category = await crud.update_category(session=session, category=category, category_data=category_data)
    await request.app.state.redis.delete(CATEGORIES_KEY)
    return category


async def delete_category(
        request: Request,
        category: Category = Depends(get_category_by_id),
        session: AsyncSession = Depends(get_db),
) -> None:
    await crud.delete_category(session=session, category=category)
    await request.app.state.redis.delete(CATEGORIES_KEY)
