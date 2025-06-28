from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderCreateSchema(BaseModel):
    product_id: UUID
    quantity: int


class OrderUpdateStatusSchema(BaseModel):
    status: str = Field(example='paid')


class OrdersSchema(BaseModel):
    id: UUID
    user_id: UUID
    total_price: Decimal
    status: str


class OrderSchema(OrdersSchema):
    cart_price: Decimal
    delivery_price: Decimal
    created_at: datetime


class ProductDataSchema(BaseModel):
    price: Decimal


class OrderItemSchema(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: Decimal


class OrderWithItemsSchema(OrderSchema):
    items: list[OrderItemSchema]
