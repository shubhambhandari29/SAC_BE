import pytest

from services.sac import claim_review_frequency_service as svc


@pytest.mark.anyio
async def test_get_frequency_remaps_filters(monkeypatch):
    def fake_sanitize(params, allowed):
        assert params == {"CustNum": "1"}
        assert allowed == svc.ALLOWED_FILTERS_DB
        return params

    async def fake_fetch(**kwargs):
        assert kwargs["filters"] == {"CustNum": "1"}
        return [{"CustNum": "1", "MthNum": 1}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_frequency({"CustomerNum": "1"})
    assert result == [{"CustomerNum": "1", "MthNum": 1}]


@pytest.mark.anyio
async def test_upsert_frequency_remaps_payload(monkeypatch):
    captured = {}

    async def fake_merge(**kwargs):
        captured["data"] = kwargs["data_list"]
        return {"count": len(kwargs["data_list"])}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)

    payload = [{"CustomerNum": "1", "MthNum": 1, "Frequency": 5}]
    result = await svc.upsert_frequency(payload)
    assert result == {"count": 1}
    assert captured["data"][0]["CustNum"] == "1"
