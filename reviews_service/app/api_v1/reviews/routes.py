from typing import Any

from fastapi import APIRouter, Depends, status

from permissions import permission_required
from .schemas import ReviewSchema
from .services import (
    create_review_service,
    get_reviews_by_product_service,
    update_review_service,
    delete_review_service,
)

router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewSchema,
)
async def create_review(
        review: dict[str, Any] = Depends(create_review_service)
):
    return review


@router.get(
    '/{product_id}',
    response_model=list[ReviewSchema],
    dependencies=[Depends(permission_required('reviews_read'))],
)
async def get_reviews_by_product(
        reviews: list[dict[str, Any]] = Depends(get_reviews_by_product_service)
):
    return reviews


@router.patch('/{product_id}', response_model=ReviewSchema)
async def update_review(
        review: dict[str, Any] = Depends(update_review_service),
):
    return review


@router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(delete_review_service)],
)
async def delete_review():
    pass
