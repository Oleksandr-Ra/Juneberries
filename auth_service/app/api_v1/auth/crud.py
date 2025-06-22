import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.schemas import UserCreateSchema
from models import User


async def get_user(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(
        select(User)
        .where(User.email == email)
    )


async def create_user(session: AsyncSession, user_data: UserCreateSchema) -> User:
    user = User(**user_data.model_dump())
    session.add(user)
    await session.commit()
    return user
