import pytest

from services.sac import hcm_users_service as svc


@pytest.mark.anyio
async def test_get_hcm_users_remaps_filters(monkeypatch):
    def fake_sanitize(params, allowed=None):
        assert params == {"CustNum": "C1"}
        return params

    async def fake_fetch(table, filters):
        assert filters == {"CustNum": "C1"}
        return [{"CustNum": "C1", "UserID": "u1"}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_hcm_users({"CustomerNum": "C1"})
    assert result == [{"CustomerNum": "C1", "UserID": "u1"}]


@pytest.mark.anyio
async def test_upsert_hcm_users_splits_payload(monkeypatch):
    calls = {"merge": None, "insert": None}

    async def fake_merge(**kwargs):
        calls["merge"] = kwargs["data_list"]

    async def fake_insert(**kwargs):
        calls["insert"] = kwargs["records"]

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)
    monkeypatch.setattr(svc, "insert_records_async", fake_insert)

    payload = [
        {"PK_Number": 1, "CustomerNum": "1", "UserID": "u1"},
        {"CustomerNum": "2", "UserID": "u2"},
    ]

    result = await svc.upsert_hcm_users(payload)
    assert result == {"message": "Transaction successful", "count": 2}

    # Remapped records should convert CustomerNum -> CustNum
    assert calls["merge"][0]["CustNum"] == "1"
    assert calls["insert"][0]["CustNum"] == "2"
