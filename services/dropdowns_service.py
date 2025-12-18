import logging
from typing import Any

from fastapi import HTTPException

from core.db_helpers import run_raw_query_async

logger = logging.getLogger(__name__)

DropdownQuery = str | tuple[str, list[Any]]

_DROPDOWN_QUERIES: dict[str, DropdownQuery] = {
    "SAC_Contact1": """
        SELECT SACName
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "SAC_Contact2": """
        SELECT SACName, EmpTitle, TelNum, EMailID
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "AcctOwner": """
        SELECT SACName, EMailID, EmpTitle, TelNum, TelExt, LANID
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "CreatedBy": """
        SELECT SACName
        FROM tblMGTUsers
        ORDER BY SACName
    """,
    "LossCtlRep1": """
        SELECT RepName, LCEmail, LCTel, LAN_ID
        FROM tblLossCtrl
        ORDER BY RepName
    """,
    "LossCtlRep2": (
        """
        SELECT RepName, Active, LCEmail
        FROM tblLossCtrl
        WHERE Active = ?
        ORDER BY RepName
        """,
        ["Yes"],
    ),
    "RiskSolMgr": """
        SELECT RepName, LCEmail, LAN_ID
        FROM tblLossCtrl
        ORDER BY RepName
    """,
    "BranchName": """
        SELECT BranchName, ReportingBranch
        FROM tblBranch
        ORDER BY BranchName
    """,
    "ServLevel": """
        SELECT [service Level], [Dollar Threshold]
        FROM tblServiceLevel
        ORDER BY SortNum
    """,
}


async def get_dropdown_values(name: str) -> list[dict[str, Any]]:
    normalized_name = name.strip()

    if not normalized_name:
        raise HTTPException(status_code=400, detail={"error": "Dropdown type is required"})

    if normalized_name.lower() == "all":
        return await get_all_dropdowns()

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


async def get_all_dropdowns() -> list[dict[str, Any]]:
    query = """
        SELECT DD_Type, DD_Value, DD_SortOrder
        FROM tbl_DropDowns
        ORDER BY DD_Type, COALESCE(DD_SortOrder, 0), DD_Value
    """
    try:
        return await run_raw_query_async(query, [])
    except Exception as exc:
        logger.warning(f"Error fetching all dropdowns: {exc}")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
