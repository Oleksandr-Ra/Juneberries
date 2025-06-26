import jwt
from fastapi import Request, HTTPException, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings


class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        route: APIRoute = request.scope.get('route')
        endpoint = getattr(route, 'endpoint', None)
        if endpoint is None:
            return await call_next(request)

        required_permission: str = getattr(endpoint, 'required_permission', None)
        if not required_permission:
            return await call_next(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

        token = auth_header.removeprefix('Bearer ').strip()
        print('---TOKEN---', token)
        payload: dict = self.decode_token(token=token)
        print('---PAYLOAD---', payload)
        permissions: list[str] = payload.get('permissions', [])
        print('---PERMISSIONS---', permissions)

        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Permission denied',
            )

        return await call_next(request)

    @staticmethod
    def decode_token(
            token: str | bytes,
            secret_key: str = settings.auth_jwt.secret_key,
            algorithm: str = settings.auth_jwt.algorithm,
    ) -> dict:
        try:
            return jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired',
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
            )
