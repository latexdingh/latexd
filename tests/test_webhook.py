"""Unit tests for latexd.webhook module."""

import json
import threading
from unittest.mock import MagicMock, patch

import pytest

import latexd.webhook as wh


@pytest.fixture(autouse=True)
def clean_webhooks():
    """Ensure a clean webhook registry for every test."""
    with wh._lock:
        wh._webhooks.clear()
    yield
    with wh._lock:
        wh._webhooks.clear()


def test_register_returns_id():
    wid = wh.register("http://example.com/hook")
    assert isinstance(wid, str)
    assert len(wid) == 16


def test_list_shows_registered():
    wh.register("http://a.com", events=["job.complete"])
    hooks = wh.list_webhooks()
    assert len(hooks) == 1
    entry = next(iter(hooks.values()))
    assert entry["url"] == "http://a.com"
    assert entry["events"] == ["job.complete"]


def test_unregister_removes_entry():
    wid = wh.register("http://b.com")
    assert wh.unregister(wid) is True
    assert wid not in wh.list_webhooks()


def test_unregister_missing_returns_false():
    assert wh.unregister("nonexistent") is False


def test_notify_calls_deliver(monkeypatch):
    delivered = []

    def fake_post(url, data, headers, timeout):
        delivered.append((url, json.loads(data)))
        return MagicMock(status_code=200)

    monkeypatch.setattr("latexd.webhook.requests.post", fake_post)
    wh.register("http://c.com", events=["job.complete"])
    wh.notify("job.complete", {"job_id": "abc"})

    # give background thread a moment
    import time; time.sleep(0.1)
    assert len(delivered) == 1
    assert delivered[0][1]["event"] == "job.complete"


def test_notify_skips_non_matching_event(monkeypatch):
    called = []
    monkeypatch.setattr("latexd.webhook.requests.post", lambda *a, **kw: called.append(1))
    wh.register("http://d.com", events=["job.complete"])
    wh.notify("job.error", {})
    import time; time.sleep(0.1)
    assert called == []


def test_sign_added_when_secret_set(monkeypatch):
    captured_headers = {}

    def fake_post(url, data, headers, timeout):
        captured_headers.update(headers)
        return MagicMock()

    monkeypatch.setattr("latexd.webhook.requests.post", fake_post)
    wh.register("http://e.com", secret="mysecret", events=["job.complete"])
    wh.notify("job.complete", {})
    import time; time.sleep(0.1)
    assert "X-Latexd-Signature" in captured_headers
