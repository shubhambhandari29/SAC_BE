from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your_secret_key"
ACCESS_TOKEN_VALIDITY = 480  # in minutes

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_VALIDITY)
    to_encode.update({"exp": expire, "user": data})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print("JWT decode error:", e)   
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )