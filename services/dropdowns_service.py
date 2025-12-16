import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import run_raw_query_async

logger = logging.getLogger(__name__)

DropdownQuery = str | tuple[str, list[Any]]

_DROPDOWN_QUERIES: dict[str, DropdownQuery] = {
    "sac_1": """
        SELECT SACName
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "sac_2": """
        SELECT SACName, EmpTitle, TelNum, EMailID
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "acct_owner": """
        SELECT SACName, EMailID, EmpTitle, TelNum, TelExt, LANID
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "created_by": """
        SELECT SACName
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "risk_solutions_1": """
        SELECT RepName, LCEmail, LCTel, LAN_ID
        FROM tblLossCtrl
        ORDER BY RepName
    """,
    "risk_solutions_2": (
        """
        SELECT RepName, Active, LCEmail
        FROM tblLossCtrl
        WHERE Active = ?
        ORDER BY RepName
        """,
        ["Yes"],
    ),
    "risk_mgr": """
        SELECT RepName, LCEmail, LAN_ID
        FROM tblLossCtrl
        ORDER BY RepName
    """,
}

_DROPDOWN_NAME_MAP: dict[str, str] = {
    "sac_contact_1": "sac_1",
    "sac_contact1": "sac_1",
    "sac_contact_2": "sac_2",
    "sac_contact2": "sac_2",
    "sac_contact": "sac_2",
    "acctowner": "acct_owner",
    "createdby": "created_by",
    "lossctlrep1": "risk_solutions_1",
    "lossctlrep_1": "risk_solutions_1",
    "lossctlrep2": "risk_solutions_2",
    "lossctlrep_2": "risk_solutions_2",
    "risksolmgr": "risk_mgr",
}


async def get_dropdown_values(name: str) -> list[dict[str, Any]]:
    normalized_name = _resolve_dropdown_name(name)
    query_def = _DROPDOWN_QUERIES.get(normalized_name)
    if not query_def:
        raise HTTPException(status_code=404, detail={"error": f"Unknown dropdown '{name}'"})

    query, params = _normalize_query_definition(query_def)

    try:
        return await run_raw_query_async(query, params)
    except Exception as exc:
        logger.warning(f"Error fetching dropdown '{name}': {exc}")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc


def _normalize_query_definition(query_def: DropdownQuery) -> tuple[str, list[Any]]:
    if isinstance(query_def, str):
        return query_def, []

    query, params = query_def
    return query, list(params)


def _resolve_dropdown_name(raw_name: str) -> str:
    normalized = raw_name.strip().lower()
    return _DROPDOWN_NAME_MAP.get(normalized, normalized)
