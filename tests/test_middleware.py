"""Tests for latexd.middleware request logging."""

import pytest
from flask import Flask

from latexd.middleware import (
    clear_request_log,
    get_request_log,
    register_middleware,
)


@pytest.fixture()
def app():
    """Minimal Flask app with middleware registered."""
    _app = Flask(__name__)
    register_middleware(_app)

    @_app.route("/ping")
    def ping():
        return "pong", 200

    @_app.route("/fail")
    def fail():
        return "oops", 500

    clear_request_log()
    yield _app
    clear_request_log()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_response_headers_present(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert "X-Duration-Ms" in resp.headers


def test_duration_header_is_numeric(client):
    client.get("/ping")
    resp = client.get("/ping")
    duration = float(resp.headers["X-Duration-Ms"])
    assert duration >= 0


def test_request_logged(client):
    client.get("/ping")
    log = get_request_log()
    assert len(log) == 1
    entry = log[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/ping"
    assert entry["status"] == 200
    assert "duration_ms" in entry
    assert "id" in entry


def test_multiple_requests_logged(client):
    client.get("/ping")
    client.get("/fail")
    log = get_request_log()
    assert len(log) == 2
    statuses = [e["status"] for e in log]
    assert 200 in statuses
    assert 500 in statuses


def test_clear_request_log(client):
    client.get("/ping")
    assert len(get_request_log()) == 1
    clear_request_log()
    assert get_request_log() == []


def test_request_ids_are_unique(client):
    for _ in range(5):
        client.get("/ping")
    ids = [e["id"] for e in get_request_log()]
    assert len(ids) == len(set(ids))
