# services/sac/sac_account_service.py

import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import fetch_records, merge_upsert_records, sanitize_filters

logger = logging.getLogger(__name__)

TABLE_NAME = "tblAcctSpecial"
ALLOWED_FILTERS = {
    "CustomerNum",
    "CustomerName",
    "Stage",
    "isSubmitted",
    "ServLevel",
    "AcctOwner",
}


async def get_sac_account(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        return fetch_records(table=TABLE_NAME, filters=filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC account List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_sac_account(data: dict[str, Any]):
    try:
        return merge_upsert_records(
            table=TABLE_NAME,
            data_list=[data],
            key_columns=["CustomerNum"],
        )
    except Exception as e:
        logger.warning(f"Upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
