from datetime import datetime, timezone
from typing import Any

from fastapi import Request, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import DeleteResult

from permissions import permission_required
from .crud import update_review, get_reviews_by_product, create_review, delete_review
from .schemas import ReviewCreateSchema, ReviewDBCreateSchema, ReviewCreatePartialSchema


async def create_review_service(
        request: Request,
        review_data: ReviewCreateSchema,
        payload: dict = Depends(permission_required('review_create')),
) -> dict[str, Any]:
    full_data = ReviewDBCreateSchema(
        **review_data.model_dump(),
        created_at=datetime.now(timezone.utc),
        user_id=payload['sub'],
    )
    db: AsyncIOMotorCollection = request.app.state.db['reviews']

    return await create_review(
        review_data=full_data,
        db=db,
    )


async def get_reviews_by_product_service(
        product_id: str,
        request: Request,
) -> list[dict[str, Any]]:
    db: AsyncIOMotorCollection = request.app.state.db['reviews']
    return await get_reviews_by_product(
        product_id=product_id,
        db=db,
    )


async def update_review_service(
        product_id: str,
        request: Request,
        review_data: ReviewCreatePartialSchema,
        payload: dict = Depends(permission_required('review_update')),
) -> dict[str, Any]:
    user_id: str = payload['sub']
    db: AsyncIOMotorCollection = request.app.state.db['reviews']

    review: dict | None = await update_review(
        product_id=product_id,
        user_id=user_id,
        review_data=review_data,
        db=db,
    )
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found')

    return review


async def delete_review_service(
        product_id: str,
        request: Request,
        payload: dict = Depends(permission_required('review_update')),
) -> None:
    user_id: str = payload['sub']
    db: AsyncIOMotorCollection = request.app.state.db['reviews']

    result: DeleteResult = await delete_review(
        product_id=product_id,
        user_id=user_id,
        db=db,
    )
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )
