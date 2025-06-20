from datetime import datetime, timezone

from fastapi import APIRouter, Request

from schemas import ReviewCreateSchema, ReviewSchema

router = APIRouter(tags=['Reviews'])


@router.post('/reviews', response_model=ReviewSchema)
async def create_review(request: Request, review: ReviewCreateSchema):
    review_dict: dict = review.dict()
    review_dict['created_at'] = datetime.now(timezone.utc)

    result = await request.app.state.db['reviews'].insert_one(review_dict)
    review_dict['_id'] = str(result.inserted_id)
    return review_dict


@router.get('/reviews',)
async def get_reviews():
    pass


@router.get('/reviews/{id}',)
async def get_review():
    pass


@router.put('/reviews/{id}',)
async def update_review():
    pass


@router.delete('/reviews/{id}',)
async def delete_review():
    pass
