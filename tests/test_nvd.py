"""sources/nvd.py 단위 테스트 — 전 요청 모킹(오프라인 안전).

고정하는 계약: NVD가 API 키를 거부하면(404 + 헤더 `message: Invalid apiKey.`)
키 없이 한 번 재시도한다. 무효 키 탓에 NVD 소스가 매 run 조용히 실패하던
2026-10 실측 장애 재발 방지. 그 밖의 오류는 기존대로 그대로 올린다.
"""
import os
import sys
from unittest import mock

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources import nvd  # noqa: E402

_CFG = {"name": "NVD", "min_cvss": 8.0}
_STATE = {"last_run": "2026-10-11T18:00:00+00:00"}
_PAYLOAD = {
    "totalResults": 1,
    "vulnerabilities": [{
        "cve": {
            "id": "CVE-2026-0001",
            "published": "2026-10-11T19:00:00.000",
            "descriptions": [{"lang": "en", "value": "Critical RCE."}],
            "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8}}]},
        }
    }],
}


def _resp(status, payload=None, headers=None):
    resp = requests.Response()
    resp.status_code = status
    resp.url = nvd.API_BASE
    resp.headers.update(headers or {})
    resp.json = lambda: payload
    return resp


def test_invalid_api_key_falls_back_to_keyless_request():
    calls = []

    def fake_get(url, **kw):
        calls.append(kw["headers"])
        if kw["headers"].get("apiKey"):
            return _resp(404, headers={"message": "Invalid apiKey."})
        return _resp(200, _PAYLOAD)

    with mock.patch.dict(os.environ, {"NVD_API_KEY": "revoked-key"}), \
            mock.patch.object(requests, "get", fake_get):
        items = nvd.fetch(_CFG, _STATE, {})

    assert calls == [{"apiKey": "revoked-key"}, {}]
    assert [it["id"] for it in items] == ["CVE-2026-0001"]


def test_fallback_keeps_keyless_headers_and_throttle_on_later_pages():
    calls = []
    page = {**_PAYLOAD, "totalResults": nvd.RESULTS_PER_PAGE + 1}

    def fake_get(url, **kw):
        calls.append((kw["headers"], kw["params"]["startIndex"]))
        if kw["headers"].get("apiKey"):
            return _resp(404, headers={"message": "Invalid apiKey."})
        return _resp(200, page)

    with mock.patch.dict(os.environ, {"NVD_API_KEY": "revoked-key"}), \
            mock.patch.object(requests, "get", fake_get), \
            mock.patch.object(nvd.time, "sleep") as sleep:
        nvd.fetch(_CFG, _STATE, {})

    assert calls == [({"apiKey": "revoked-key"}, 0), ({}, 0), ({}, nvd.RESULTS_PER_PAGE)]
    sleep.assert_called_once_with(6)


def test_other_404_is_raised_without_retry():
    calls = []

    def fake_get(url, **kw):
        calls.append(kw["headers"])
        return _resp(404, headers={"message": "Invalid lastModStartDate."})

    with mock.patch.dict(os.environ, {"NVD_API_KEY": "valid-key"}), \
            mock.patch.object(requests, "get", fake_get):
        with pytest.raises(requests.HTTPError):
            nvd.fetch(_CFG, _STATE, {})

    assert len(calls) == 1


def test_keyless_404_is_raised_without_retry():
    calls = []

    def fake_get(url, **kw):
        calls.append(kw["headers"])
        return _resp(404, headers={"message": "Invalid apiKey."})

    env = {k: v for k, v in os.environ.items() if k != "NVD_API_KEY"}
    with mock.patch.dict(os.environ, env, clear=True), \
            mock.patch.object(requests, "get", fake_get):
        with pytest.raises(requests.HTTPError):
            nvd.fetch(_CFG, _STATE, {})

    assert calls == [{}]
