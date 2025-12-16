# services/sac/sac_account_service.py

import logging
import re
from datetime import date, datetime
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
    "IsSubmitted",
    "ServLevel",
    "AcctOwner",
    "BranchName",
}
_DATE_FIELDS = {
    "OnBoardDate",
    "DateCreated",
    "DiscDate",
    "TermDate",
    "DateNotif",
    "RenewLetterDt",
    "NCMStartDt",
    "NCMEndDt",
}
_DATE_OUTPUT_FORMAT = "%d-%m-%Y"


async def get_sac_account(query_params: dict[str, Any]):
    try:
        filters = sanitize_filters(query_params, ALLOWED_FILTERS)
        branch_filter = filters.pop("BranchName", None)

        if not branch_filter:
            records = await fetch_records_async(table=TABLE_NAME, filters=filters)
            return _format_date_fields(records)

        branch_terms = [term for term in re.split(r"[ ,&]+", str(branch_filter)) if term.strip()]

        # Fall back to simple filtering if nothing usable came from the branch filter.
        if not branch_terms:
            records = await fetch_records_async(table=TABLE_NAME, filters=filters)
            return _format_date_fields(records)

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

        records = await run_raw_query_async(query, list(params))
        return _format_date_fields(records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except Exception as e:
        logger.warning(f"Error fetching SAC account List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


async def upsert_sac_account(data: dict[str, Any]):
    try:
        normalized_data = _normalize_date_fields_for_upsert(data)
        return await merge_upsert_records_async(
            table=TABLE_NAME,
            data_list=[normalized_data],
            key_columns=["CustomerNum"],
        )
    except Exception as e:
        logger.warning(f"Upsert failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e


def _format_date_fields(records: list[dict[str, Any]]):
    for record in records:
        for field in _DATE_FIELDS:
            if field not in record:
                continue
            record[field] = _format_date_value(record.get(field))
    return records


def _normalize_date_fields_for_upsert(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    for field in _DATE_FIELDS:
        if field not in normalized:
            continue
        normalized[field] = _parse_upsert_date_value(normalized[field])
    return normalized


def _format_date_value(value: Any):
    if value in (None, ""):
        return value

    if isinstance(value, datetime):
        return value.strftime(_DATE_OUTPUT_FORMAT)

    if isinstance(value, date):
        return value.strftime(_DATE_OUTPUT_FORMAT)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value

        iso_candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
        try:
            parsed = datetime.fromisoformat(iso_candidate)
            return parsed.strftime(_DATE_OUTPUT_FORMAT)
        except ValueError:
            date_part = text
            for sep in ("T", " "):
                if sep in date_part:
                    date_part = date_part.split(sep, 1)[0]
                    break
            try:
                parsed = datetime.strptime(date_part, "%Y-%m-%d")
                return parsed.strftime(_DATE_OUTPUT_FORMAT)
            except ValueError:
                return value

    return value


def _parse_upsert_date_value(value: Any):
    if value in (None, ""):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value

        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue

        if text.endswith("Z"):
            try:
                return datetime.fromisoformat(text[:-1]).date()
            except ValueError:
                return value

    return value