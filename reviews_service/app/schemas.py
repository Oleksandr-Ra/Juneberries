from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    product_id: int
    user_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewSchema(ReviewCreateSchema):
    id: str = Field(alias='_id')
    created_at: datetime
