import pytest
from fastapi import HTTPException

from services.sac import sac_policies_service as svc


@pytest.mark.anyio
async def test_get_sac_policies(monkeypatch):
    def fake_sanitize(params, allowed):
        assert allowed == svc.ALLOWED_FILTERS
        return params

    async def fake_fetch(**kwargs):
        assert kwargs["filters"] == {"CustomerNum": "1"}
        return [{"PolicyNum": "P1"}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_sac_policies({"CustomerNum": "1"})
    assert result == [{"PolicyNum": "P1"}]


@pytest.mark.anyio
async def test_upsert_sac_policies(monkeypatch):
    async def fake_merge(**kwargs):
        assert kwargs["data_list"][0]["CustomerNum"] == "1"
        return {"message": "ok"}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)
    result = await svc.upsert_sac_policies({"CustomerNum": "1"})
    assert result == {"message": "ok"}


@pytest.mark.anyio
async def test_update_field_for_all_policies_runs_query(monkeypatch):
    executed = {}

    class DummyCursor:
        def execute(self, query, params):
            executed["query"] = query.strip()
            executed["params"] = params

    class DummyConn:
        def __init__(self):
            self.cursor_obj = DummyCursor()
            self.committed = False

        def cursor(self):
            return self.cursor_obj

        def commit(self):
            self.committed = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_db_connection():
        return DummyConn()

    async def fake_run_in_threadpool(fn):
        return fn()

    monkeypatch.setattr(svc, "db_connection", fake_db_connection)
    monkeypatch.setattr(svc, "run_in_threadpool", fake_run_in_threadpool)

    payload = {
        "fieldName": "Stage",
        "fieldValue": "Bound",
        "updateVia": "CustomerNum",
        "updateViaValue": "1",
    }
    result = await svc.update_field_for_all_policies(payload)
    assert result == {"message": "Update successful"}
    assert "UPDATE" in executed["query"]
    assert executed["params"] == ("Bound", "1")


@pytest.mark.anyio
async def test_update_field_for_all_policies_invalid_field():
    payload = {
        "fieldName": "Bad",
        "updateVia": "CustomerNum",
        "fieldValue": "x",
        "updateViaValue": "1",
    }
    with pytest.raises(HTTPException):
        await svc.update_field_for_all_policies(payload)


@pytest.mark.anyio
async def test_get_premium_builds_query(monkeypatch):
    def fake_sanitize(params, allowed):
        assert params["PolicyStatus"] == "Active"
        return params

    async def fake_run_raw(query, params):
        return [{"Premium": 50}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "run_raw_query_async", fake_run_raw)

    result = await svc.get_premium({"CustomerNum": "1"})
    assert result == 50
