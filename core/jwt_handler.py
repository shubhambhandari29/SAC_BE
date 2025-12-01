# core/jwt_handler.py

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException

from core.config import settings

SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_VALIDITY = settings.ACCESS_TOKEN_VALIDITY


def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_VALIDITY)
    to_encode.update({"exp": expire, "user": data})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=403, detail="Invalid token") from exc


def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=403, detail="Could not verify credentials") from exc
