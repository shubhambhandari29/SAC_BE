import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import (
    delete_records_async,
    fetch_records_async,
    merge_upsert_records_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblDistribute_DeductBill"
ALLOWED_FILTERS = {"CustomerNum", "EMailAddress"}


async def get_distribution(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        return await fetch_records_async(table=TABLE_NAME, filters=filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching Deduct Bill Distribution - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_distribution(data_list: list[dict[str, Any]]):
    try:
        return await merge_upsert_records_async(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=["CustomerNum", "EMailAddress"],
        )
    except Exception as e:
        logger.warning(f"Upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def delete_distribution(data_list: list[dict[str, Any]]):
    try:
        return await delete_records_async(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=["CustomerNum", "EMailAddress"],
        )
    except Exception as e:
        logger.warning(f"Deletion failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
