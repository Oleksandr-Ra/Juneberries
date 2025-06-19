import uuid

from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    product_id: uuid.UUID
    user_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    text: str = ''


class ReviewSchema(ReviewCreateSchema):
    id: str = Field(alias='_id')
