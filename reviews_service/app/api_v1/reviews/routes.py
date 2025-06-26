from datetime import datetime, timezone

from fastapi import APIRouter, Request

from schemas import ReviewCreateSchema, ReviewSchema

router = APIRouter(tags=['Reviews'])


@router.post('/reviews', response_model=ReviewSchema)
async def add_review(request: Request, review: ReviewCreateSchema):
    review_dict: dict = review.dict()
    review_dict['created_at'] = datetime.now(timezone.utc)

    result = await request.app.state.db['reviews'].insert_one(review_dict)
    review_dict['_id'] = str(result.inserted_id)
    return review_dict


@router.get('/reviews/{product_id}',)
async def get_reviews_by_product():
    pass


@router.patch('/reviews/{product_id}',)
async def refresh_review():
    pass


@router.delete('/reviews/{product_id}',)
async def delete_review():
    pass
