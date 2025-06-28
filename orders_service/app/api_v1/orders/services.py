from decimal import Decimal
from uuid import UUID

from fastapi import Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import Order, OrderItem
from utils import fetch_product_data
from . import crud
from .schemas import OrderCreateSchema, ProductDataSchema, OrderUpdateStatusSchema


async def create_order(
        user_id: UUID,
        token: str,
        order_data: list[OrderCreateSchema],
        session: AsyncSession,
) -> Order:
    order_items = []
    cart_price = Decimal('0.00')

    for product in order_data:
        product_data: ProductDataSchema = await fetch_product_data(product_id=product.product_id, token=token)

        order_item = OrderItem(
            product_id=product.product_id,
            quantity=product.quantity,
            unit_price=Decimal(product_data.price)
        )
        order_items.append(order_item)
        cart_price += order_item.quantity * order_item.unit_price

    delivery_price = Decimal('5.00')
    total_price = cart_price + delivery_price

    new_order = {
        'user_id': user_id,
        'total_price': total_price,
        'cart_price': cart_price,
        'delivery_price': delivery_price,
        'status': 'ordered',
        'items': order_items,
    }

    return await crud.create_order(session=session, order_data=new_order)


async def get_orders(
        session: AsyncSession = Depends(get_db),
) -> list[Order]:
    return await crud.get_orders(session=session)


async def get_order_by_id(
        order_id: UUID = Path,
        session: AsyncSession = Depends(get_db),
) -> Order:
    order: Order | None = await crud.get_order(session=session, order_id=order_id)
    if order:
        return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Order {order_id} not found!',
    )


async def update_order(
        order_data: OrderUpdateStatusSchema,
        order: Order = Depends(get_order_by_id),
        session: AsyncSession = Depends(get_db),
) -> Order:
    return await crud.update_order(session=session, order=order, order_data=order_data)


async def delete_order(
        order: Order = Depends(get_order_by_id),
        session: AsyncSession = Depends(get_db),
) -> None:
    await crud.delete_order(session=session, order=order)
