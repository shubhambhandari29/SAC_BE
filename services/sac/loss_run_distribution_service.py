import logging
from typing import Any

from fastapi import HTTPException

from core.date_utils import format_records_dates, normalize_payload_list
from core.db_helpers import (
    delete_records_async,
    fetch_records_async,
    insert_records_async,
    merge_upsert_records_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblDistribute_LossRun"
ALLOWED_FILTERS = {"CustomerNum", "EMailAddress"}


async def get_distribution(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        records = await fetch_records_async(table=TABLE_NAME, filters=filters)
        return format_records_dates(records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching Loss Run Distribution List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_distribution(data_list: list[dict[str, Any]]):
    try:
        normalized = normalize_payload_list(data_list)
        to_update: list[dict[str, Any]] = []
        to_insert: list[dict[str, Any]] = []

        for record in normalized:
            pk_value = record.get("PK_Number")
            if pk_value in (None, ""):
                sanitized = {k: v for k, v in record.items() if k != "PK_Number"}
                if sanitized:
                    to_insert.append(sanitized)
            else:
                to_update.append(record)

        if to_update:
            await merge_upsert_records_async(
                table=TABLE_NAME,
                data_list=to_update,
                key_columns=["PK_Number"],
                exclude_key_columns_from_insert=True,
            )

        if to_insert:
            await insert_records_async(table=TABLE_NAME, records=to_insert)

        return {"message": "Transaction successful", "count": len(normalized)}
    except Exception as e:
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def delete_distribution(data_list: list[dict[str, Any]]):
    try:
        return await delete_records_async(
            table=TABLE_NAME,
            data_list=data_list,
            key_columns=["CustomerNum", "AttnTo"],
        )
    except Exception as e:
        logger.warning(f"Deletion failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
