"""Integration tests for /metrics routes."""

import pytest
from flask import Flask
from latexd.metrics import MetricsStore
from latexd.metrics_routes import metrics_bp


@pytest.fixture
def isolated_store():
    return MetricsStore()


@pytest.fixture
def client(isolated_store):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["METRICS_STORE"] = isolated_store
    app.register_blueprint(metrics_bp)
    with app.test_client() as c:
        yield c, isolated_store


def test_metrics_empty(client):
    c, _ = client
    resp = c.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_requests"] == 0
    assert data["total_compilations"] == 0


def test_metrics_after_activity(client):
    c, store = client
    store.record_request()
    store.record_compilation("svg", latency_ms=55.0)
    store.record_cache_hit()
    resp = c.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_requests"] == 1
    assert data["total_compilations"] == 1
    assert data["cache_hits"] == 1
    assert data["format_counts"] == {"svg": 1}
    assert data["avg_latency_ms"] == 55.0


def test_metrics_reset(client):
    c, store = client
    store.record_request()
    store.record_compilation("png")
    resp = c.post("/metrics/reset")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    resp2 = c.get("/metrics")
    d2 = resp2.get_json()
    assert d2["total_requests"] == 0
    assert d2["total_compilations"] == 0


def test_metrics_format_counts_accumulate(client):
    c, store = client
    store.record_compilation("svg")
    store.record_compilation("svg")
    store.record_compilation("png")
    resp = c.get("/metrics")
    data = resp.get_json()
    assert data["format_counts"]["svg"] == 2
    assert data["format_counts"]["png"] == 1


def test_uptime_present(client):
    c, _ = client
    resp = c.get("/metrics")
    data = resp.get_json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0
