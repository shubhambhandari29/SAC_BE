import pytest
from fastapi import HTTPException

from services.sac import sac_account_service as svc


@pytest.mark.anyio
async def test_get_sac_account_without_branch(monkeypatch):
    calls = {}

    def fake_sanitize(params, allowed):
        assert allowed == svc.ALLOWED_FILTERS
        return {"CustomerNum": "1"}

    async def fake_fetch(table, filters):
        calls["filters"] = filters
        assert table == svc.TABLE_NAME
        return [{"CustomerNum": "1", "OnBoardDate": "2024-01-05 00:00:00"}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_sac_account({"CustomerNum": "1"})
    assert result == [{"CustomerNum": "1", "OnBoardDate": "05-01-2024"}]
    assert calls["filters"] == {"CustomerNum": "1"}


@pytest.mark.anyio
async def test_get_sac_account_with_branch(monkeypatch):
    captured = {}

    def fake_sanitize(params, allowed):
        return {"BranchName": "NY & LA", "Stage": "Active"}

    async def fake_raw(query, params):
        captured["query"] = query
        captured["params"] = params
        return [
            {"CustomerNum": "1", "BranchName": "NY", "OnBoardDate": "2024-02-10T00:00:00Z"}
        ]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "run_raw_query_async", fake_raw)

    result = await svc.get_sac_account({})
    assert result == [{"CustomerNum": "1", "BranchName": "NY", "OnBoardDate": "10-02-2024"}]
    assert "BranchName LIKE ?" in captured["query"]
    assert captured["params"] == ["Active", "NY%", "LA%"]


@pytest.mark.anyio
async def test_get_sac_account_handles_null_onboard_date(monkeypatch):
    def fake_sanitize(params, allowed):
        return {}

    async def fake_fetch(table, filters):
        return [{"CustomerNum": "1", "OnBoardDate": None}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_sac_account({})
    assert result == [{"CustomerNum": "1", "OnBoardDate": None}]


@pytest.mark.anyio
async def test_get_sac_account_invalid_filter(monkeypatch):
    def fake_sanitize(params, allowed):
        raise ValueError("bad field")

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)

    with pytest.raises(HTTPException) as exc:
        await svc.get_sac_account({})

    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_upsert_sac_account(monkeypatch):
    async def fake_merge(**kwargs):
        return {"message": "ok"}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)

    result = await svc.upsert_sac_account({"CustomerNum": "1"})
    assert result == {"message": "ok"}
