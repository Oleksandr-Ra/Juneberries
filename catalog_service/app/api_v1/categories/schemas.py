from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBaseSchema(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=100, example='category')]


class CategoryCreateSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(CategoryCreateSchema):
    pass


class CategoryUpdatePartialSchema(CategoryCreateSchema):
    name: Annotated[str | None, Field(min_length=2, max_length=100, example='user')] = None


class CategoriesSchema(CategoryBaseSchema):
    id: UUID


class CategorySchema(CategoriesSchema):
    created_at: datetime
