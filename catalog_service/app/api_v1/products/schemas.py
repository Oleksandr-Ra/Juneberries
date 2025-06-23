from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBaseSchema(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=200, example='product name')]
    price: Decimal
    category_id: UUID


class ProductCreateSchema(ProductBaseSchema):
    description: str = Field(example='description')


class ProductUpdateSchema(ProductCreateSchema):
    pass


class ProductUpdatePartialSchema(ProductCreateSchema):
    name: Annotated[str | None, Field(min_length=2, max_length=200, example='product name')] = None
    description: Annotated[str | None, Field(example='description')] = None
    price: Decimal | None = None
    category_id: UUID | None = None


class ProductsSchema(ProductBaseSchema):
    id: UUID


class ProductSchema(ProductsSchema):
    description: str
    created_at: datetime
