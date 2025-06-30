from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher, exceptions

from config import settings

ph = PasswordHasher()


def get_password_hash(password: str) -> str:
    return ph.hash(password)


def verify_password(hashed: str, password: str) -> bool:
    try:
        ph.verify(hash=hashed, password=password)
        return True
    except exceptions.VerifyMismatchError:
        return False
    except exceptions.VerificationError:
        return False


def encode_jwt(
        payload: dict,
        expire_timedelta: timedelta,
        secret_key: str = settings.auth_jwt.secret_key,
        algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + expire_timedelta
    to_encode.update(exp=expire, iat=now)
    return jwt.encode(payload=to_encode, key=secret_key, algorithm=algorithm)


def decode_jwt(
        token: str | bytes,
        secret_key: str = settings.auth_jwt.secret_key,
        algorithm: str = settings.auth_jwt.algorithm,
):
    return jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
