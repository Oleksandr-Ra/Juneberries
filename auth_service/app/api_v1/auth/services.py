from datetime import timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserCreateSchema, AuthLoginSchema, AccessRefreshTokensSchema
from . import crud

from config import settings
from db import get_db
from models import User
from utils import get_password_hash, verify_password, encode_jwt, decode_jwt

ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, reg_data: UserCreateSchema) -> User:
        if await crud.check_user_by_email(session=self.session, email=reg_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='A user with this email already exists'
            )
        reg_data.password_hash = get_password_hash(reg_data.password_hash)
        return await crud.create_user(session=self.session, user_data=reg_data)

    async def login_user(self, login_data: AuthLoginSchema) -> AccessRefreshTokensSchema:
        user = await crud.get_user_by_email(self.session, login_data.email)
        if not user or not verify_password(hashed=user.password_hash, password=login_data.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password',
            )
        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> AccessRefreshTokensSchema:
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        return AccessRefreshTokensSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def _create_access_token(self, user: User) -> str:
        access_payload = {
            'sub': str(user.id),
            'role_id': user.role_id,
            'permissions': [p.code for p in user.role.permissions],
            'type': ACCESS_TOKEN_TYPE,
        }
        return encode_jwt(
            payload=access_payload,
            expire_timedelta=timedelta(minutes=settings.auth_jwt.access_token_expire_minutes),
        )

    def _create_refresh_token(self, user: User) -> str:
        refresh_payload = {
            'sub': str(user.id),
            'type': REFRESH_TOKEN_TYPE,
        }
        return encode_jwt(
            payload=refresh_payload,
            expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
        )

    def decode_token(self, token: str) -> dict:
        try:
            return decode_jwt(token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired',
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
            )

    def validate_token_type(self, payload: dict, expected_type: str) -> None:
        actual_type = payload.get('type')
        if actual_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid token type {actual_type!r}, expected {expected_type!r}',
            )

    async def get_user_from_token(self, payload: dict) -> User:
        user_id = UUID(payload.get('sub'))
        user = await crud.get_user(session=self.session, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
            )
        return user

    async def refresh_access_token(self, refresh_token: str) -> AccessRefreshTokensSchema:
        payload: dict = self.decode_token(token=refresh_token)
        self.validate_token_type(payload=payload, expected_type=REFRESH_TOKEN_TYPE)
        user = await self.get_user_from_token(payload=payload)
        return self._generate_tokens(user=user)

    async def get_current_user_info(self, access_token: str) -> User:
        payload: dict = self.decode_token(token=access_token)
        self.validate_token_type(payload=payload, expected_type=ACCESS_TOKEN_TYPE)
        return await self.get_user_from_token(payload=payload)


def get_auth_service(
    session: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(session=session)
