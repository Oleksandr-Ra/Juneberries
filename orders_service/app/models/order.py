import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Enum, TIMESTAMP, func, Numeric, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class OrderStatus(str, enum.Enum):
    created = 'created'
    processing = 'processing'
    shipped = 'shipped'
    delivered = 'delivered'
    cancelled = 'cancelled'


class Order(Base):
    __tablename__ = 'orders_service'

    user_id: Mapped[int]
    status: Mapped[str] = mapped_column(
        Enum(OrderStatus, values_callable=lambda obj: [e.value for e in obj], name='order_status_enum'),
        default=OrderStatus.created.value,
        server_default=OrderStatus.created.value,
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )

    items: Mapped[list['OrderItem']] = relationship(back_populates='order', cascade='all, delete')


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_id: Mapped[int] = mapped_column(ForeignKey('orders_service.id'))
    product_id: Mapped[int]
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped['Order'] = relationship(back_populates='items')
