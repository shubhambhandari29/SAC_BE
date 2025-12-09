# services/sac/sac_account_service.py

import logging
import re
from typing import Any

from fastapi import HTTPException

from core.db_helpers import (
    fetch_records_async,
    merge_upsert_records_async,
    run_raw_query_async,
    sanitize_filters,
)

logger = logging.getLogger(__name__)

TABLE_NAME = "tblAcctSpecial"
ALLOWED_FILTERS = {
    "CustomerNum",
    "CustomerName",
    "Stage",
    "isSubmitted",
    "ServLevel",
    "AcctOwner",
    "BranchName",
}


async def get_sac_account(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        branch_filter = filters.pop("BranchName", None)

        if not branch_filter:
            return await fetch_records_async(table=TABLE_NAME, filters=filters)

        branch_terms = [
            term for term in re.split(r"[ ,&]+", str(branch_filter)) if term.strip()
        ]

        # Fall back to simple filtering if nothing usable came from the branch filter.
        if not branch_terms:
            return await fetch_records_async(table=TABLE_NAME, filters=filters)

        clauses: list[str] = []
        params: list[Any] = []

        for key, value in filters.items():
            clauses.append(f"{key} = ?")
            params.append(value)

        branch_clauses = ["BranchName LIKE ?" for _ in branch_terms]
        clauses.append(f"({' OR '.join(branch_clauses)})")
        params.extend(f"{term}%" for term in branch_terms)

        query = f"SELECT * FROM {TABLE_NAME}"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        return await run_raw_query_async(query, list(params))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"EError fetching SAC account List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
   
   
 
async def upsert_sac_account(data):
    """
    Update row if already exists, else insert row into tblAcctSpecial
    """
 
    try:
        cursor = conn.cursor()
 
        # Assuming `CustomerNum` is the primary key / unique identifier
        merge_query = f"""
        MERGE INTO tblAcctSpecial AS target
        USING (SELECT {", ".join(['? AS ' + col for col in data.keys()])}) AS source
        ON target.CustomerNum = source.CustomerNum
        WHEN MATCHED THEN
            UPDATE SET {", ".join([f"{col} = source.{col}" for col in data.keys() if col != 'CustomerNum'])}
        WHEN NOT MATCHED THEN
            INSERT ({", ".join(data.keys())})
            VALUES ({", ".join(['source.' + col for col in data.keys()])});
        """
 
        values = list(data.values())
        cursor.execute(merge_query, values)
        conn.commit()
 
        return {"message": "Transaction successful"}
    except Exception as e:
        conn.rollback()
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})