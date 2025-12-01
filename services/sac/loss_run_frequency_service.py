# services/sac/loss_run_frequency_service.py

import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import fetch_records, merge_upsert_records, sanitize_filters

logger = logging.getLogger(__name__)

TABLE_NAME = "tblLossRunFrequency"
ORDER_BY_COLUMN = "MthNum"
ALLOWED_FILTERS = {"CustomerNum", "MthNum"}


async def get_frequency(query_params: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Fetch account(s) from tblLossRunFrequency.
    If query_params is provided, filters by given key/value.
    Returns a list of dicts (records).
    """
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        records = fetch_records(
            table=TABLE_NAME,
            filters=filters,
            order_by=ORDER_BY_COLUMN,
        )
        return records
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching Loss Run frequency List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_frequency(data_list: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Takes an array of maps as data.
    Updates row if already exists, else inserts row into tblLossRunFrequency.
    Matching key: CustomerNum + MthNum.
    """
    try:
        result = merge_upsert_records(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=["CustomerNum", "MthNum"],
        )
        return result
    except Exception as e:
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
