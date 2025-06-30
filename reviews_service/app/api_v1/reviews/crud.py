from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult, DeleteResult

from .schemas import ReviewDBCreateSchema, ReviewCreatePartialSchema


async def create_review(
        review_data: ReviewDBCreateSchema,
        db: AsyncIOMotorCollection,
) -> dict[str, Any]:
    review_dict: dict[str, Any] = review_data.model_dump()
    review: InsertOneResult = await db.insert_one(review_dict)

    review_dict['_id'] = str(review.inserted_id)
    return review_dict


async def get_reviews_by_product(
        product_id: str,
        db: AsyncIOMotorCollection,
) -> list[dict[str, Any]]:
    reviews: list = await db.find({'product_id': product_id}).to_list(length=1000)
    for review in reviews:
        review['_id'] = str(review['_id'])
    return reviews


async def update_review(
        product_id: str,
        user_id: str,
        review_data: ReviewCreatePartialSchema,
        db: AsyncIOMotorCollection,
) -> dict[str, Any] | None:
    review: dict | None = await db.find_one_and_update(
        filter={'product_id': product_id, 'user_id': user_id},
        update={'$set': review_data.model_dump(exclude_unset=True)},
        return_document=ReturnDocument.AFTER,
    )
    if review is None:
        return None
    review['_id'] = str(review['_id'])
    return review


async def delete_review(
        product_id: str,
        user_id: str,
        db: AsyncIOMotorCollection,
) -> DeleteResult:
    return await db.delete_one(
        filter={'product_id': product_id, 'user_id': user_id},
    )
