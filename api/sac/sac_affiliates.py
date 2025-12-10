from fastapi import APIRouter, Request
from services.sac.sac_affiliates_service import get_affiliates as get_affiliates_service
from services.sac.sac_affiliates_service import upsert_affiliates as upsert_affiliates_service

router = APIRouter()

@router.get("/")
async def get_affiliates(request: Request):
    return await get_affiliates_service(dict(request.query_params))
    
@router.post("/upsert")
async def upsert_affiliates(request: Request):
    data = await request.json()
    return await upsert_affiliates_service(data)
