import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import Category


class Product(Base):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('categories.id'))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )

    category: Mapped['Category'] = relationship(back_populates='products')
