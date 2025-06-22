from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api_v1.auth.schemas import (
    UserSchema,
    UserCreateSchema,
    AccessRefreshTokensSchema,
    AuthLoginSchema,
)
from api_v1.auth.services import AuthService, get_auth_service

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/register', response_model=UserSchema)
async def register(
        reg_data: UserCreateSchema,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register_user(reg_data=reg_data)


@router.post('/login', response_model=AccessRefreshTokensSchema)
async def login(
        login_data: AuthLoginSchema,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login_user(login_data=login_data)


@router.get('/me', response_model=UserSchema)
async def current_user_info(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user_info(access_token=credentials.credentials)


@router.post('/refresh', response_model=AccessRefreshTokensSchema)
async def refresh(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_access_token(refresh_token=credentials.credentials)
