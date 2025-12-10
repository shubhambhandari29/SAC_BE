from fastapi import APIRouter, Request
from services.sac.hcm_users_service import get_hcm_users as get_hcm_users_service
from services.sac.hcm_users_service import upsert_hcm_users as upsert_hcm_users_service

router = APIRouter()

@router.get("/")
async def get_hcm_users(request: Request):
    return await get_hcm_users_service(dict(request.query_params))
    
@router.post("/upsert")
async def upsert_hcm_users(request: Request):
    data = await request.json()
    return await upsert_hcm_users_service(data)
