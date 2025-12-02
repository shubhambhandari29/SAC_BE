import logging
from typing import Any, Dict, List

from fastapi import HTTPException

from core.db_helpers import (
    fetch_records_async,
    merge_upsert_records_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblHCMUsers"
KEY_COLUMNS = ["CustNum", "UserID"]
FILTER_MAP = {"CustomerNum": "CustNum"}


def _remap_keys(payload: Dict[str, Any]) -> Dict[str, Any]:
    remapped = payload.copy()
    if "CustomerNum" in remapped:
        remapped["CustNum"] = remapped.pop("CustomerNum")
    return remapped


def _restore_customer_num(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for record in records:
        if "CustNum" in record:
            record["CustomerNum"] = record.pop("CustNum")
    return records


async def get_hcm_users(query_params: Dict[str, Any]):
    try:
        normalized = {FILTER_MAP.get(key, key): value for key, value in query_params.items()}
        filters = sanitize_filters(normalized)
        records = await fetch_records_async(table=TABLE_NAME, filters=filters)
        return _restore_customer_num(records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching HCM users - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_hcm_users(data_list: List[Dict[str, Any]]):
    try:
        payload = [_remap_keys(item) for item in data_list]
        return await merge_upsert_records_async(
            table=TABLE_NAME,
            data_list=payload,
            key_columns=KEY_COLUMNS,
        )
    except Exception as e:
        logger.warning(f"HCM users upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
