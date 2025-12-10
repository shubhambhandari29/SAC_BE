import pytest

from services.sac import loss_run_frequency_service as svc


@pytest.mark.anyio
async def test_get_frequency(monkeypatch):
    def fake_sanitize(params, allowed):
        assert params == {"CustNum": "1"}
        return params

    async def fake_fetch(**kwargs):
        assert kwargs["filters"] == {"CustNum": "1"}
        return [{"CustNum": "1", "MthNum": 3}]

    monkeypatch.setattr(svc, "sanitize_filters", fake_sanitize)
    monkeypatch.setattr(svc, "fetch_records_async", fake_fetch)

    result = await svc.get_frequency({"CustomerNum": "1"})
    assert result == [{"CustomerNum": "1", "MthNum": 3}]


@pytest.mark.anyio
async def test_upsert_frequency(monkeypatch):
    captured = {}

    async def fake_merge(**kwargs):
        captured["data"] = kwargs["data_list"]
        return {"count": 1}

    monkeypatch.setattr(svc, "merge_upsert_records_async", fake_merge)

    payload = [{"CustomerNum": "1", "MthNum": 3}]
    result = await svc.upsert_frequency(payload)
    assert result == {"count": 1}
    assert captured["data"][0]["CustNum"] == "1"
