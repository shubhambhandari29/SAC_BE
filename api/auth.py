# api/auth.py
from fastapi import APIRouter, Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer
from services.auth_service import (login_user, get_current_user_from_token, logout_user, refresh_user_token)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login")
async def login(request: Request, response: Response):
    return await login_user(request, response)

@router.get("/me")
async def get_current_user(request: Request):
    return await get_current_user_from_token(request)

@router.post("/logout")
async def logout(response: Response):
    return await logout_user(response)

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, token: str = Depends(oauth2_scheme)):
    return await refresh_user_token(request, response, token)
