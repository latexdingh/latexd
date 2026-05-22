"""Integration tests for webhook REST routes."""

import pytest
from flask import Flask

import latexd.webhook as wh
from latexd.webhook_routes import bp


@pytest.fixture(autouse=True)
def clean_webhooks():
    with wh._lock:
        wh._webhooks.clear()
    yield
    with wh._lock:
        wh._webhooks.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app.test_client()


def test_list_empty(client):
    r = client.get("/webhooks/")
    assert r.status_code == 200
    assert r.get_json() == {}


def test_register_webhook(client):
    r = client.post("/webhooks/", json={"url": "http://example.com/cb"})
    assert r.status_code == 201
    data = r.get_json()
    assert "id" in data
    assert data["url"] == "http://example.com/cb"


def test_register_missing_url(client):
    r = client.post("/webhooks/", json={})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_register_bad_url_scheme(client):
    r = client.post("/webhooks/", json={"url": "ftp://bad.com"})
    assert r.status_code == 400


def test_register_invalid_events_type(client):
    r = client.post("/webhooks/", json={"url": "http://x.com", "events": "not-a-list"})
    assert r.status_code == 400


def test_delete_webhook(client):
    r = client.post("/webhooks/", json={"url": "http://y.com"})
    wid = r.get_json()["id"]
    r2 = client.delete(f"/webhooks/{wid}")
    assert r2.status_code == 200
    assert r2.get_json()["deleted"] == wid
    assert wh.list_webhooks() == {}


def test_delete_nonexistent(client):
    r = client.delete("/webhooks/doesnotexist")
    assert r.status_code == 404


def test_list_shows_registered_webhook(client):
    client.post("/webhooks/", json={"url": "http://z.com", "events": ["job.complete"]})
    r = client.get("/webhooks/")
    hooks = r.get_json()
    assert len(hooks) == 1
    entry = next(iter(hooks.values()))
    assert entry["url"] == "http://z.com"
