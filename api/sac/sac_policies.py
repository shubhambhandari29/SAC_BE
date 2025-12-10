from fastapi import APIRouter, Request
from services.sac.sac_policies_service import get_sac_policies as get_sac_policies_service
from services.sac.sac_policies_service import upsert_sac_policies as upsert_sac_policies_service
from services.sac.sac_policies_service import update_field_for_all_policies as update_field_for_all_policies_service
from services.sac.sac_policies_service import get_premium as get_premium_service

router = APIRouter()

@router.get("/")
async def get_sac_policies(request: Request):
    return await get_sac_policies_service(dict(request.query_params))
    
@router.post("/upsert")
async def upsert_sac_policies(request: Request):
    data = await request.json()
    return await upsert_sac_policies_service(data)

@router.post("/update_field_for_all_policies")
async def upsert_sac_account(request: Request):
    data = await request.json()
    return await update_field_for_all_policies_service(data)

@router.get("/get_premium")
async def get_premium(request: Request):
    return await get_premium_service(dict(request.query_params))
