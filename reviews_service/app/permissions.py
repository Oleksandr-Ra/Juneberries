from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import settings

security = HTTPBearer(description='Enter your JWT token here')


def permission_required(required_permission: str):
    def check_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        token = credentials.credentials

        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.auth_jwt.secret_key,
                algorithms=[settings.auth_jwt.algorithm]
            )
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

        permissions = payload.get('permissions', [])

        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Permission denied. Required: {required_permission}',
            )

        return payload
    return check_permission
