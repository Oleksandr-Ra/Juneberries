import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import OrderItem


class Order(Base):
    __tablename__ = 'orders'

    user_id: Mapped[uuid.UUID]
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cart_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )

    items: Mapped[list['OrderItem']] = relationship(back_populates='order', cascade='all, delete')
