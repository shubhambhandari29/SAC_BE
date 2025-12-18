import pytest
from fastapi import HTTPException

from services import dropdowns_service as svc


@pytest.mark.anyio
async def test_get_dropdown_values_known(monkeypatch):
    captured = {}

    async def fake_run(query, params):
        captured["query"] = query
        captured["params"] = params
        return [{"SACName": "Alex"}]

    monkeypatch.setattr(svc, "run_raw_query_async", fake_run)

    result = await svc.get_dropdown_values("SAC_Contact1")

    assert result == [{"SACName": "Alex"}]
    assert "FROM tblMGTUsers" in captured["query"]
    assert captured["params"] == []


@pytest.mark.anyio
async def test_get_dropdown_values_with_params(monkeypatch):
    captured = {}

    async def fake_run(query, params):
        captured["query"] = query
        captured["params"] = params
        return [{"RepName": "Chris"}]

    monkeypatch.setattr(svc, "run_raw_query_async", fake_run)

    result = await svc.get_dropdown_values("LossCtlRep2")

    assert result == [{"RepName": "Chris"}]
    assert "WHERE Active = ?" in captured["query"]
    assert captured["params"] == ["Yes"]


@pytest.mark.anyio
async def test_get_dropdown_values_dynamic(monkeypatch):
    captured = {}

    async def fake_run(query, params):
        captured["query"] = query
        captured["params"] = params
        return [{"DD_Value": "Value1", "DD_SortOrder": 1}]

    monkeypatch.setattr(svc, "run_raw_query_async", fake_run)

    result = await svc.get_dropdown_values("AccomType")

    assert result == [{"DD_Value": "Value1", "DD_SortOrder": 1}]
    assert "FROM tbl_DropDowns" in captured["query"]
    assert captured["params"] == ["AccomType"]


@pytest.mark.anyio
async def test_get_dropdown_values_missing_type():
    with pytest.raises(HTTPException) as exc:
        await svc.get_dropdown_values("  ")

    assert exc.value.status_code == 400
