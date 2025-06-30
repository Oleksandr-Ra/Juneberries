import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    name: str = Field(min_length=3, max_length=100, example='John')
    email: EmailStr = Field(max_length=254, example='john@example.com')
    role_id: int


class UserCreateSchema(UserBaseSchema):
    password_hash: str = Field(min_length=6, alias='password', example='password123#')


class UserSchema(UserBaseSchema):
    id: uuid.UUID
    created_at: datetime


class AuthLoginSchema(BaseModel):
    email: EmailStr = Field(max_length=254, example='john@example.com')
    password_hash: str = Field(min_length=6, alias='password', example='password123#')


class AccessRefreshTokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    type: str = 'Bearer'
