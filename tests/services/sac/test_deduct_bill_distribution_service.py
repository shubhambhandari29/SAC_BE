import pytest

from services.sac import deduct_bill_distribution_service as svc


@pytest.mark.anyio
async def test_get_distribution(monkeypatch):
    def fake_sanitize(params, allowed=None):
        return params

    async def fake_fetch(**kwargs):
        assert kwargs["filters"] == {"CustomerNum": "1"}
        return [{"CustomerNum": "1"}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_distribution({"CustomerNum": "1"})
    assert result == [{"CustomerNum": "1"}]


@pytest.mark.anyio
async def test_upsert_distribution(monkeypatch):
    captured = {}

    async def fake_merge(**kwargs):
        captured["data"] = kwargs["data_list"]
        return {"count": 1}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)
    await svc.upsert_distribution([{"CustomerNum": "1", "EMailAddress": "a"}])
    assert captured["data"][0]["CustomerNum"] == "1"


@pytest.mark.anyio
async def test_delete_distribution(monkeypatch):
    captured = {}

    async def fake_delete(**kwargs):
        captured["data"] = kwargs["data_list"]
        return {"count": 1}

    monkeypatch.setattr(svc, "delete_records_async", fake_delete)
    await svc.delete_distribution([{"CustomerNum": "1", "EMailAddress": "a"}])
    assert captured["data"][0]["CustomerNum"] == "1"
