# core/db_helpers.py

import logging
import re
from collections.abc import Iterable
from typing import Any

import pandas as pd

from db import db_connection

logger = logging.getLogger(__name__)

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _ensure_safe_identifier(identifier: str) -> None:
    if not identifier or not _IDENTIFIER_PATTERN.match(identifier):
        raise ValueError(f"Invalid column or table name: {identifier}")


def sanitize_filters(
    query_params: dict[str, Any] | None,
    allowed_fields: Iterable[str] | None = None,
) -> dict[str, Any]:
    """
    Validate incoming filters against an allow-list and identifier rules.
    """
    if not query_params:
        return {}

    sanitized: dict[str, Any] = {}
    allowed = set(allowed_fields) if allowed_fields is not None else None
    disallowed: list[str] = []

    for key, value in query_params.items():
        if allowed is not None and key not in allowed:
            disallowed.append(key)
            continue

        _ensure_safe_identifier(key)
        sanitized[key] = value

    if disallowed:
        raise ValueError(f"Invalid filter field(s): {', '.join(sorted(disallowed))}")

    return sanitized


def build_select_query(
    table: str,
    filters: dict[str, Any] | None = None,
    order_by: str | None = None,
) -> tuple[str, list[Any]]:
    """
    Build a parametrized SELECT query like:
    SELECT * FROM <table> WHERE col1 = ? AND col2 = ? ORDER BY <order_by>
    """
    _ensure_safe_identifier(table)
    base_query = f"SELECT * FROM {table}"
    params: list[Any] = []

    if filters:
        clauses: list[str] = []
        for key, value in filters.items():
            _ensure_safe_identifier(key)
            clauses.append(f"{key} = ?")
            params.append(value)

        if clauses:
            base_query += " WHERE " + " AND ".join(clauses)

    if order_by:
        _ensure_safe_identifier(order_by)
        base_query += f" ORDER BY {order_by}"

    return base_query, params


def fetch_records(
    table: str,
    filters: dict[str, Any] | None = None,
    order_by: str | None = None,
) -> list[dict[str, Any]]:
    """
    Run a SELECT on <table> using filters and optional ORDER BY,
    return rows as list[dict].
    """
    query, params = build_select_query(table, filters, order_by)

    with db_connection() as conn:
        df = pd.read_sql(query, conn, params=params)

    # Replace NaN with None for JSON
    df = df.astype(object).where(pd.notna(df), None)
    return df.to_dict(orient="records")


def run_raw_query(query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    """
    Generic helper to run any SELECT query (used later e.g. for search queries).
    """
    with db_connection() as conn:
        df = pd.read_sql(query, conn, params=params or [])

    df = df.astype(object).where(pd.notna(df), None)
    return df.to_dict(orient="records")


def merge_upsert_records(
    table: str,
    data_list: list[dict[str, Any]],
    key_columns: list[str],
) -> dict[str, Any]:
    """
    Generic MERGE-based upsert helper.

    - table: target table name
    - data_list: list of rows (dicts) to upsert
    - key_columns: columns used to match existing rows (ON clause)
    """
    if not data_list:
        return {"message": "No data provided", "count": 0}

    _ensure_safe_identifier(table)

    from db import db_connection as _db_connection  # avoid circular import confusion

    try:
        with _db_connection() as conn:
            cursor = conn.cursor()

            for data in data_list:
                columns = list(data.keys())
                for column in columns:
                    _ensure_safe_identifier(column)

                using_cols = ", ".join([f"? AS {col}" for col in columns])

                on_clauses = [f"target.{key} = source.{key}" for key in key_columns]
                on_clause = " AND ".join(on_clauses)
                for key in key_columns:
                    _ensure_safe_identifier(key)

                update_cols = [col for col in columns if col not in key_columns]
                update_set = (
                    ", ".join([f"{col} = source.{col}" for col in update_cols])
                    if update_cols
                    else ""
                )
                update_section = ""
                if update_set:
                    update_section = f"""
WHEN MATCHED THEN
    UPDATE SET {update_set}
"""

                merge_query = f"""
MERGE INTO {table} AS target
USING (SELECT {using_cols}) AS source
ON {on_clause}
{update_section}WHEN NOT MATCHED THEN
    INSERT ({", ".join(columns)})
    VALUES ({", ".join(["source." + col for col in columns])});
"""
                values = list(data.values())
                cursor.execute(merge_query, values)

            conn.commit()

    except Exception as e:
        # Try to rollback if connection is still open
        try:
            conn.rollback()
        except Exception:
            # If rollback itself fails, just log and move on
            logger.error("Rollback failed after error in merge_upsert_records", exc_info=True)

        logger.error(f"Error during merge_upsert_records on {table}: {e}", exc_info=True)
        # Let the caller (service) decide how to surface this (HTTPException, etc.)
        raise

    return {"message": "Transaction successful", "count": len(data_list)}


def delete_records(
    table: str,
    data_list: list[dict[str, Any]],
    key_columns: list[str],
) -> dict[str, Any]:
    """
    Generic delete helper.
    Deletes rows matching key_columns from data_list.

    Example:
        key_columns = ["CustomerNum", "EMailAddress"]
    """
    if not data_list:
        return {"message": "No data provided for deletion", "count": 0}

    _ensure_safe_identifier(table)

    from db import db_connection as _db_connection

    conn = None
    try:
        with _db_connection() as conn:
            cursor = conn.cursor()

            for data in data_list:
                # Validate keys exist
                for key in key_columns:
                    if key not in data:
                        raise ValueError(f"{key} is required for deletion")

                where_clause_parts = []
                for key in key_columns:
                    _ensure_safe_identifier(key)
                    where_clause_parts.append(f"{key} = ?")

                where_clause = " AND ".join(where_clause_parts)
                delete_query = f"DELETE FROM {table} WHERE {where_clause}"

                values = [data[key] for key in key_columns]
                cursor.execute(delete_query, values)

            conn.commit()

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                logger.error("Rollback failed in delete_records", exc_info=True)
        logger.error(f"Error deleting records from {table}: {e}", exc_info=True)
        raise

    return {"message": "Deletion successful", "count": len(data_list)}
