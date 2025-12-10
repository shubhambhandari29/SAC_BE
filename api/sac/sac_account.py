from fastapi import APIRouter, Request
from services.sac.sac_account_service import get_sac_account as get_sac_account_service
from services.sac.sac_account_service import upsert_sac_account as upsert_sac_account_service

router = APIRouter()

@router.get("/")
async def get_sac_account(request: Request):
    return await get_sac_account_service(dict(request.query_params))
    
@router.post("/upsert")
async def upsert_sac_account(request: Request):
    data = await request.json()
    return await upsert_sac_account_service(data)
