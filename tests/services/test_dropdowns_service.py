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

    result = await svc.get_dropdown_values("sac_1")

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

    result = await svc.get_dropdown_values("risk_solutions_2")

    assert result == [{"RepName": "Chris"}]
    assert "WHERE Active = ?" in captured["query"]
    assert captured["params"] == ["Yes"]


@pytest.mark.anyio
async def test_get_dropdown_values_invalid_name():
    with pytest.raises(HTTPException) as exc:
        await svc.get_dropdown_values("unknown")

    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_get_dropdown_values_alias(monkeypatch):
    async def fake_run(query, params):
        return [{"SACName": "Alex"}]

    monkeypatch.setattr(svc, "run_raw_query_async", fake_run)

    result = await svc.get_dropdown_values("SAC_Contact_1")

    assert result == [{"SACName": "Alex"}]
