import logging
from decimal import Decimal
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from connections import get_producer
from db import get_db, async_session
from models import Order, OrderItem
from permissions import permission_required
from utils import fetch_product_data
from . import crud
from .schemas import OrderCreateSchema, ProductDataSchema, OrderUpdateStatusSchema

logger = logging.getLogger(__name__)


async def create_order(
        products_list: list[OrderCreateSchema],
        producer: AIOKafkaProducer = Depends(get_producer),
        payload: dict = Depends(permission_required('order_create')),
        session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    order_items = []
    cart_price = Decimal('0.00')

    for product in products_list:
        # get price from Product
        product_data: ProductDataSchema = await fetch_product_data(
            product_id=product.product_id,
            token=payload['token'],
        )

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
        'user_id': payload['sub'],
        'total_price': total_price,
        'cart_price': cart_price,
        'delivery_price': delivery_price,
        'status': 'processing',
        'items': order_items,
    }

    order = await crud.create_order(session=session, order_data=new_order)
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Could not create order.')

    message = {
        'order_id': str(order.id),
        'delivery_price': float(order.delivery_price),
        'cart_price': float(order.cart_price),
    }
    await producer.send(topic=settings.kafka.order_create_topic, value=message)

    return {'message': 'Your order has been accepted for processing.'}


async def get_orders(
        session: AsyncSession = Depends(get_db),
) -> list[Order]:
    return await crud.get_orders(session=session)


async def get_order_by_id(
        order_id: UUID = Path(...),
        session: AsyncSession = Depends(get_db),
) -> Order:
    order: Order | None = await crud.get_order(session=session, order_id=order_id)
    if order:
        return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Order {order_id} not found!',
    )


async def update_order_status(
        order_data: OrderUpdateStatusSchema,
        order: Order = Depends(get_order_by_id),
        session: AsyncSession = Depends(get_db),
) -> Order:
    return await crud.update_order(
        session=session,
        order=order,
        order_data=order_data.model_dump(exclude_unset=True),
    )


async def delete_order(
        order: Order = Depends(get_order_by_id),
        session: AsyncSession = Depends(get_db),
) -> None:
    await crud.delete_order(session=session, order=order)


async def process_message(message_data: dict) -> None:
    order_id: str | None = message_data.get('order_id')
    if order_id is None:
        return None

    update_order_data = {
        'delivery_price': message_data['delivery_price'],
        'cart_price': message_data['cart_price'],
        'total_price': message_data['total_price'],
        'status': message_data['status'],
    }

    async with async_session() as session:
        order: Order | None = await crud.get_order(session=session, order_id=UUID(order_id))
        if order is None:
            logger.error(f'Order {order_id} not found! Create order process not finished!')

        await crud.update_order(
            session=session,
            order=order,
            order_data=update_order_data,
        )
        logger.info(f'Order {order_id} successfully updated!')
