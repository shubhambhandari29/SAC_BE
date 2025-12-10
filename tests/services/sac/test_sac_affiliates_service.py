import pytest

from services.sac import sac_affiliates_service as svc


@pytest.mark.anyio
async def test_get_affiliates(monkeypatch):
    async def fake_fetch(table, filters):
        assert table == svc.TABLE_NAME
        assert filters == {"CustomerNum": "1"}
        return [{"AffiliateName": "Alpha"}]

    def fake_sanitize(params, allowed=None):
        return params

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_affiliates({"CustomerNum": "1"})
    assert result == [{"AffiliateName": "Alpha"}]


@pytest.mark.anyio
async def test_upsert_affiliates_splits_records(monkeypatch):
    calls = {"merge": None, "insert": None}

    async def fake_merge(**kwargs):
        calls["merge"] = kwargs["data_list"]

    async def fake_insert(**kwargs):
        calls["insert"] = kwargs["records"]

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)
    monkeypatch.setattr(svc, "insert_records_async", fake_insert)

    payload = [
        {"PK_Number": 1, "CustomerNum": "1", "AffiliateName": "Alpha"},
        {"CustomerNum": "2", "AffiliateName": "Beta"},
    ]

    result = await svc.upsert_affiliates(payload)
    assert result == {"message": "Transaction successful", "count": 2}
    assert calls["merge"] == [payload[0]]
    assert calls["insert"] == [payload[1]]
