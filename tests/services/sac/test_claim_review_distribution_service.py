import pytest

from services.sac import claim_review_distribution_service as svc


@pytest.mark.anyio
async def test_get_distribution(monkeypatch):
    def fake_sanitize(params, allowed=None):
        assert allowed == svc.ALLOWED_FILTERS
        return params

    async def fake_fetch(**kwargs):
        assert kwargs["table"] == svc.TABLE_NAME
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
        return {"count": len(kwargs["data_list"])}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)

    payload = [{"CustomerNum": "1", "EMailAddress": "a@example.com"}]
    result = await svc.upsert_distribution(payload)
    assert result == {"count": 1}
    assert captured["data"] == payload


@pytest.mark.anyio
async def test_delete_distribution(monkeypatch):
    captured = {}

    async def fake_delete(**kwargs):
        captured["data"] = kwargs["data_list"]
        return {"deleted": len(kwargs["data_list"])}

    monkeypatch.setattr(svc, "delete_records_async", fake_delete)

    payload = [{"CustomerNum": "1", "EMailAddress": "a@example.com"}]
    result = await svc.delete_distribution(payload)
    assert result == {"deleted": 1}
    assert captured["data"] == payload
