from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import Order
from permissions import permission_required
from . import services
from .schemas import OrderWithItemsSchema, OrderSchema, OrderCreateSchema, OrdersSchema

router = APIRouter(prefix='/orders', tags=['Orders'])


@router.post(
    '',
    response_model=OrderWithItemsSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
        order_data: list[OrderCreateSchema],
        payload: dict = Depends(permission_required('order_create')),
        session: AsyncSession = Depends(get_db),
):
    order: Order = await services.create_order(
        user_id=payload['sub'],
        token=payload['token'],
        order_data=order_data,
        session=session,
    )
    return order


@router.get(
    '',
    response_model=list[OrdersSchema],
    dependencies=[Depends(permission_required('orders_read'))],
)
async def get_orders(
        orders: list[Order] = Depends(services.get_orders),
):
    return orders


@router.get(
    '/{id}',
    response_model=OrderSchema,
    dependencies=[Depends(permission_required('order_read'))],
)
async def get_order(
        order: Order = Depends(services.get_order_by_id),
):
    return order


@router.patch(
    '/{id}',
    response_model=OrderSchema,
    dependencies=[Depends(permission_required('order_update'))],
)
async def update_order_status(
        order: Order = Depends(services.update_order),
):
    return order


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(permission_required('order_delete')),
        Depends(services.delete_order),
    ],
)
async def delete_order():
    pass
