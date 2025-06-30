from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Order
from .schemas import OrderUpdateStatusSchema


async def get_order(session: AsyncSession, order_id: UUID) -> Order | None:
    return await session.get(Order, order_id)


async def get_orders(session: AsyncSession) -> list[Order]:
    result = await session.scalars(
        select(Order)
        .order_by(Order.created_at.desc())
    )
    return list(result.all())


async def create_order(session: AsyncSession, order_data: dict) -> Order:
    order = Order(**order_data)
    session.add(order)
    await session.commit()
    return order


async def update_order(
        session: AsyncSession,
        order: Order,
        order_data: OrderUpdateStatusSchema,
) -> Order:
    for key, value in order_data.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    await session.commit()
    return order


async def delete_order(session: AsyncSession, order: Order) -> None:
    await session.delete(order)
    await session.commit()
