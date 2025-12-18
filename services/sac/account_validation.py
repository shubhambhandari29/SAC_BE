"""Validation helpers for SAC account payloads."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

ROLE_PRIORITY = {"Underwriter": 0, "Director": 1, "Admin": 2}

# Minimum role required to edit a specific field. Fields missing here are treated
# as available to every role.
FIELD_MIN_ROLE: dict[str, str] = {
    "CustomerNum": "Underwriter",
    "CustomerName": "Underwriter",
    "OnBoardDate": "Underwriter",
    "BranchName": "Underwriter",
    "DateNotif": "Admin",
    "TermDate": "Admin",
    "TermCode": "Admin",
}

REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("CustomerNum", "Customer Number is mandatory."),
    ("CustomerName", "Account Name is mandatory."),
    ("OnBoardDate", "On Board Date is mandatory."),
    ("BranchName", "Branch Name is mandatory."),
)

INACTIVE_DEPENDENCIES: tuple[tuple[str, str], ...] = (
    ("DateNotif", "Notification Date is mandatory when account is Inactive."),
    ("TermDate", "Termination Date is mandatory when account is Inactive."),
    ("TermCode", "Termination Reason is mandatory when account is Inactive."),
)

ZERO_REQUIRED_LEVELS = {
    "Decuctible Billing - Special Accounts",
    "Loss Run",
    "Deductible Billing - Paragon",
    "Inactive",
}


def _role_value(role: str | None) -> int:
    return ROLE_PRIORITY.get(role or "Underwriter", 0)


def _is_enabled(field: str, role: str | None) -> bool:
    min_role = FIELD_MIN_ROLE.get(field)
    if not min_role:
        return True
    return _role_value(role) >= _role_value(min_role)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _error(field: str, code: str, message: str) -> dict[str, str]:
    return {"field": field, "code": code, "message": message}


def _coerce_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _service_level_conflict(payload: dict[str, Any]) -> bool:
    level = payload.get("ServLevel")
    if not level:
        return False

    total_value = _coerce_number(payload.get("TotalPrem"))

    if level in ZERO_REQUIRED_LEVELS:
        return total_value is None or total_value != 0

    if total_value is None:
        return False

    if level == "Comprehensive":
        return total_value < 750000
    if level == "Enhanced":
        return total_value < 500000 or total_value > 750000
    if level == "Essential":
        return total_value < 250000 or total_value > 500000
    if level == "Primary":
        return total_value < 150000 or total_value > 250000
    if level == "Exception":
        return total_value < 0 or total_value > 150000

    return False


def validate_account_payload(payload: dict[str, Any], role: str | None) -> list[dict[str, str]]:
    """
    Validate the SAC account payload and return a list of error dicts.
    """

    normalized_role = role or "Underwriter"
    errors: list[dict[str, str]] = []

    for field, message in REQUIRED_FIELDS:
        if _is_enabled(field, normalized_role) and not _has_value(payload.get(field)):
            errors.append(_error(field, "REQUIRED", message))

    if payload.get("AcctStatus") == "Inactive":
        for field, message in INACTIVE_DEPENDENCIES:
            if _is_enabled(field, normalized_role) and not _has_value(payload.get(field)):
                errors.append(_error(field, "REQUIRED", message))

    override = payload.get("ServiceLevelOverride") in (True, "true", "True", "1", 1)
    if not override and _service_level_conflict(payload):
        errors.append(
            _error(
                "ServLevel",
                "SERVICE_LEVEL_CONFLICT",
                "Total Active Policy Premium is in conflict with Service Level.",
            )
        )

    return errors
