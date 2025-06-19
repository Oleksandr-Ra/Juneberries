import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import Order


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[uuid.UUID]
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped['Order'] = relationship(back_populates='items')
