from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    product_id: str = Field(example='3fa85f64-5717-4562-b3fc-2c963f66afa6')
    rating: int = Field(ge=1, le=5, example=4)
    text: str = ''


class ReviewDBCreateSchema(ReviewCreateSchema):
    user_id: str = Field(example='3fa85f64-5717-4562-b3fc-2c963f66afa6')
    created_at: datetime


class ReviewSchema(ReviewDBCreateSchema):
    id: str = Field(alias='_id', example='6860c92a14287a4dae7681bf')


class ReviewCreatePartialSchema(BaseModel):
    rating: Annotated[int | None, Field(ge=1, le=5, example=5)] = None
    text: Annotated[str | None, Field(example='Some review text')] = None
