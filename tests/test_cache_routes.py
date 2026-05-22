"""Integration tests for cache management REST routes."""

import pytest
from flask import Flask

import latexd.cache_routes as cache_routes_module
from latexd.cache import RenderCache
from latexd.cache_routes import cache_bp


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Replace the module-level cache with a temp-dir-backed instance."""
    fresh = RenderCache(cache_dir=tmp_path)
    monkeypatch.setattr(cache_routes_module, "_cache", fresh)
    return fresh


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(cache_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_stats_empty(client):
    resp = client.get("/cache/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["entries"] == 0


def test_stats_after_insert(client, isolated_cache):
    isolated_cache.set("x", "svg", b"data")
    resp = client.get("/cache/stats")
    assert resp.get_json()["entries"] == 1


def test_clear(client, isolated_cache):
    isolated_cache.set("x", "svg", b"d1")
    isolated_cache.set("y", "png", b"d2")
    resp = client.delete("/cache/clear")
    assert resp.status_code == 200
    assert resp.get_json()["removed"] == 2
    assert isolated_cache.size == 0


def test_invalidate_entry(client, isolated_cache):
    isolated_cache.set("x^2", "svg", b"data")
    resp = client.delete(
        "/cache/entry", json={"snippet": "x^2", "format": "svg"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["invalidated"] is True


def test_invalidate_missing_entry(client):
    resp = client.delete(
        "/cache/entry", json={"snippet": "nothing", "format": "svg"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["invalidated"] is False


def test_invalidate_missing_snippet(client):
    resp = client.delete("/cache/entry", json={"format": "svg"})
    assert resp.status_code == 400


def test_invalidate_invalid_format(client):
    resp = client.delete(
        "/cache/entry", json={"snippet": "x", "format": "pdf"}
    )
    assert resp.status_code == 400
