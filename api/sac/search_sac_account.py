from fastapi import APIRouter, Request
from services.sac.search_sac_account_service import search_sac_account_records as get_sac_account_records_service

router = APIRouter()

@router.get("/")
async def get_sac_account_records(request: Request):
    return await get_sac_account_records_service(dict(request.query_params)['search_by'])