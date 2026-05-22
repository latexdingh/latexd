"""Tests for latexd.snippet_store and the /snippets REST routes."""

from __future__ import annotations

import pytest
from flask import Flask

import latexd.snippet_store as store
from latexd.snippet_store import DuplicateSnippetError
from latexd.snippet_routes import snippet_bp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_registry():
    store.clear()
    yield
    store.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(snippet_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Unit tests — snippet_store
# ---------------------------------------------------------------------------

def test_add_returns_entry():
    entry = store.add("quad", r"\quad", "horizontal space")
    assert entry.name == "quad"
    assert entry.body == r"\quad"
    assert entry.description == "horizontal space"


def test_list_shows_added():
    store.add("a", r"\alpha")
    store.add("b", r"\beta")
    names = {s.name for s in store.list_snippets()}
    assert names == {"a", "b"}


def test_duplicate_name_raises():
    store.add("dup", r"\pi")
    with pytest.raises(DuplicateSnippetError):
        store.add("dup", r"\pi")


def test_get_existing():
    store.add("x", r"x^2")
    assert store.get("x") is not None


def test_get_missing_returns_none():
    assert store.get("nonexistent") is None


def test_remove_existing():
    store.add("rm", r"\rm")
    assert store.remove("rm") is True
    assert store.get("rm") is None


def test_remove_missing_returns_false():
    assert store.remove("ghost") is False


def test_update_changes_body():
    store.add("u", r"\alpha")
    entry = store.update("u", r"\beta", "updated")
    assert entry.body == r"\beta"
    assert entry.description == "updated"


def test_update_missing_raises():
    with pytest.raises(KeyError):
        store.update("missing", r"\gamma")


# ---------------------------------------------------------------------------
# Integration tests — /snippets routes
# ---------------------------------------------------------------------------

def test_list_empty(client):
    r = client.get("/snippets/")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_snippet(client):
    r = client.post("/snippets/", json={"name": "frac", "body": r"\frac{a}{b}"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["name"] == "frac"


def test_create_missing_name(client):
    r = client.post("/snippets/", json={"body": r"\pi"})
    assert r.status_code == 400


def test_create_duplicate_returns_409(client):
    client.post("/snippets/", json={"name": "dup", "body": r"\pi"})
    r = client.post("/snippets/", json={"name": "dup", "body": r"\pi"})
    assert r.status_code == 409


def test_get_snippet_route(client):
    client.post("/snippets/", json={"name": "s", "body": r"\sigma"})
    r = client.get("/snippets/s")
    assert r.status_code == 200
    assert r.get_json()["name"] == "s"


def test_get_missing_snippet_returns_404(client):
    r = client.get("/snippets/nope")
    assert r.status_code == 404


def test_update_snippet_route(client):
    client.post("/snippets/", json={"name": "upd", "body": r"\alpha"})
    r = client.put("/snippets/upd", json={"body": r"\omega"})
    assert r.status_code == 200
    assert r.get_json()["body"] == r"\omega"


def test_delete_snippet_route(client):
    client.post("/snippets/", json={"name": "del", "body": r"\delta"})
    r = client.delete("/snippets/del")
    assert r.status_code == 204
    assert client.get("/snippets/del").status_code == 404
