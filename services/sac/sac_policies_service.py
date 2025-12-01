# services/sac/sac_policies_service.py

import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import fetch_records, merge_upsert_records, sanitize_filters
from db import db_connection

logger = logging.getLogger(__name__)

TABLE_NAME = "tblPolicies"
ALLOWED_FILTERS = {"CustomerNum", "PolicyNum", "PolMod"}
ALLOWED_UPDATE_FIELDS = {"ServLevel", "Stage", "AcctOwner", "isSubmitted"}
ALLOWED_UPDATE_FILTERS = {"CustomerNum", "PolicyNum", "PolMod"}


async def get_sac_policies(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        return fetch_records(table=TABLE_NAME, filters=filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC policies List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_sac_policies(data: dict[str, Any]):
    try:
        return merge_upsert_records(
            table=TABLE_NAME,
            data_list=[data],
            key_columns=["CustomerNum", "PolicyNum", "PolMod"],
        )
    except Exception as e:
        logger.warning(f"Upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def update_field_for_all_policies(data: dict[str, Any]):
    """
    Example:
        UPDATE tblPolicies
        SET fieldName = fieldValue
        WHERE updateVia = updateViaValue
    """
    field_name = data.get("fieldName")
    update_via = data.get("updateVia")

    if field_name not in ALLOWED_UPDATE_FIELDS:
        raise HTTPException(status_code=400, detail={"error": "Invalid fieldName"})

    if update_via not in ALLOWED_UPDATE_FILTERS:
        raise HTTPException(status_code=400, detail={"error": "Invalid updateVia"})

    if "fieldValue" not in data or "updateViaValue" not in data:
        raise HTTPException(
            status_code=400, detail={"error": "fieldValue and updateViaValue are required"}
        )

    try:
        query = f"""
            UPDATE {TABLE_NAME}
            SET {field_name} = ?
            WHERE {update_via} = ?
        """

        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (data["fieldValue"], data["updateViaValue"]))
            conn.commit()

        return {"message": "Update successful"}

    except Exception as e:
        logger.error(f"Error updating policies field: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
