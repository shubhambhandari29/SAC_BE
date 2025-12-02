# services/sac/deduct_bill_frequency_service.py

import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import (
    fetch_records_async,
    merge_upsert_records_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblDeductBillFrequency"
ORDER_BY_COLUMN = "MthNum"
ALLOWED_FILTERS = {"CustomerNum", "MthNum"}


async def get_frequency(query_params: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        return await fetch_records_async(table=TABLE_NAME, filters=filters, order_by=ORDER_BY_COLUMN)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching Deduct Bill frequency List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_frequency(data_list: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        return await merge_upsert_records_async(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=["CustomerNum", "MthNum"],
        )
    except Exception as e:
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
