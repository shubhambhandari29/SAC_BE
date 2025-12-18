import logging
from typing import Any

from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from core.date_utils import format_records_dates, normalize_payload_dates, parse_date_input
from core.db_helpers import (
    fetch_records_async,
    insert_records_async,
    merge_upsert_records_async,
    run_raw_query_async,
    sanitize_filters,
)
from db import db_connection

logger = logging.getLogger(__name__)

TABLE_NAME = "tblPolicies"
PRIMARY_KEY = "PK_Number"
ALLOWED_FILTERS = {"CustomerNum", "PolicyNum", "PolMod"}
PREMIUM_ALLOWED_FILTERS = {"CustomerNum", "PolicyNum", "PolMod", "PolicyStatus"}


async def get_sac_policies(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        records = await fetch_records_async(table=TABLE_NAME, filters=filters)
        return format_records_dates(records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC policies List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_sac_policies(data: dict[str, Any]):
    try:
        normalized = normalize_payload_dates(data)
        pk_value = normalized.get(PRIMARY_KEY)

        if pk_value in (None, ""):
            sanitized_record = {k: v for k, v in normalized.items() if k != PRIMARY_KEY}
            if sanitized_record:
                await insert_records_async(table=TABLE_NAME, records=[sanitized_record])
        else:
            await merge_upsert_records_async(
                table=TABLE_NAME,
                data_list=[normalized],
                key_columns=[PRIMARY_KEY],
                exclude_key_columns_from_insert=True,
            )

        return {"message": "Transaction successful", "count": 1}
    except Exception as e:
        logger.warning(f"Upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def update_field_for_all_policies(data: dict[str, Any]):
    field_name = data.get("fieldName")
    update_via = data.get("updateVia")

    if "fieldValue" not in data or "updateViaValue" not in data:
        raise HTTPException(status_code=400, detail={"error": "Missing required values"})

    field_value = data["fieldValue"]
    if isinstance(field_value, str):
        parsed = parse_date_input(field_value)
        field_value = parsed

    query = f"""
        UPDATE {TABLE_NAME}
        SET {field_name} = ?
        WHERE {update_via} = ?
    """

    def _execute_update():
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (field_value, data["updateViaValue"]))
            conn.commit()
        return {"message": "Update successful"}

    try:
        return await run_in_threadpool(_execute_update)
    except Exception as e:
        logger.error(f"Error updating policies field: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def get_premium(query_params: dict[str, Any]):
    """
    Fetch sum of premium of all active policies from tblPolicies.
    """

    try:
        filters_input = dict(query_params)
        filters_input["PolicyStatus"] = "Active"
        filters = sanitize_filters(filters_input, PREMIUM_ALLOWED_FILTERS)

        clauses = []
        params = []
        for key, value in filters.items():
            clauses.append(f"{key} = ?")
            params.append(value)

        query = "SELECT COALESCE(SUM(PremiumAmt), 0) AS Premium FROM tblPolicies"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        rows = await run_raw_query_async(query, params)
        premium_value = rows[0]["Premium"] if rows else 0
        return premium_value

    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC policy premium - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
