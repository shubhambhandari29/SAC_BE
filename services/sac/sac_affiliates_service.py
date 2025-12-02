import logging
from typing import Any, Dict, List

from fastapi import HTTPException

from core.db_helpers import (
    fetch_records_async,
    merge_upsert_records_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblAffiliates"
KEY_COLUMNS = ["CustomerNum", "AffiliateName"]


async def get_affiliates(query_params: Dict[str, Any]):
    try:
        filters = sanitize_filters(query_params)
        return await fetch_records_async(table=TABLE_NAME, filters=filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC affiliates - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_affiliates(data_list: List[Dict[str, Any]]):
    try:
        return await merge_upsert_records_async(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=KEY_COLUMNS,
        )
    except Exception as e:
        logger.warning(f"SAC affiliates upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
