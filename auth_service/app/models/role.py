from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import User
    from models import Permission


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    users: Mapped[list['User']] = relationship(back_populates='role')
    permissions: Mapped[list['Permission']] = relationship(
        secondary='roles_permissions',
        back_populates='roles',
    )
