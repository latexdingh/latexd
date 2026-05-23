"""Tests for the PreviewStore and preview routes."""

import pytest
from flask import Flask
from latexd.preview import PreviewStore
from latexd.preview_routes import preview_bp, get_preview_store
import latexd.preview_routes as pr_module


@pytest.fixture()
def store():
    return PreviewStore(max_entries=4)


@pytest.fixture()
def client(store):
    app = Flask(__name__)
    app.register_blueprint(preview_bp)
    pr_module._store = store
    with app.test_client() as c:
        yield c
    pr_module._store = None


# --- Unit tests for PreviewStore ---

def test_get_miss(store):
    assert store.get("x", "svg") is None


def test_put_and_get(store):
    store.put("\\alpha", "svg", b"<svg/>")
    entry = store.get("\\alpha", "svg")
    assert entry is not None
    assert entry.data == b"<svg/>"


def test_hit_count_increments(store):
    store.put("\\beta", "png", b"\x89PNG")
    store.get("\\beta", "png")
    store.get("\\beta", "png")
    assert store.get("\\beta", "png").hit_count == 3


def test_remove_existing(store):
    store.put("x", "svg", b"data")
    assert store.remove("x", "svg") is True
    assert store.get("x", "svg") is None


def test_remove_missing(store):
    assert store.remove("nope", "svg") is False


def test_clear_returns_count(store):
    store.put("a", "svg", b"1")
    store.put("b", "png", b"2")
    assert store.clear() == 2
    assert store.stats()["entries"] == 0


def test_eviction_when_full(store):
    for i in range(4):
        store.put(f"snippet{i}", "svg", b"x")
    store.put("extra", "svg", b"y")  # should evict oldest
    assert store.stats()["entries"] == 4


def test_to_dict_keys(store):
    entry = store.put("z", "svg", b"<svg/>")
    d = entry.to_dict()
    assert {"format", "size_bytes", "created_at", "hit_count"} == set(d.keys())


def test_put_same_key_overwrites(store):
    """Putting the same snippet/format twice should overwrite the entry."""
    store.put("\\delta", "svg", b"<svg>old</svg>")
    store.put("\\delta", "svg", b"<svg>new</svg>")
    entry = store.get("\\delta", "svg")
    assert entry is not None
    assert entry.data == b"<svg>new</svg>"
    # Overwriting should not inflate the entry count
    assert store.stats()["entries"] == 1


# --- Route tests ---

def test_stats_empty(client):
    resp = client.get("/preview/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["entries"] == 0


def test_clear_route(client, store):
    store.put("a", "svg", b"data")
    resp = client.post("/preview/clear")
    assert resp.status_code == 200
    assert resp.get_json()["cleared"] == 1


def test_invalidate_route(client, store):
    store.put("\\gamma", "png", b"data")
    resp = client.post("/preview/invalidate", json={"snippet": "\\gamma", "format": "png"})
    assert resp.status_code == 200
    assert resp.get_json()["removed"] is True


def test_invalidate_missing_snippet(client):
    resp = client.post("/preview/invalidate", json={"format": "svg"})
    assert resp.status_code == 400
