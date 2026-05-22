"""Integration tests for latexd auth_routes blueprint."""

import pytest
from flask import Flask

import latexd.auth as auth_module
from latexd.auth_routes import auth_bp


@pytest.fixture(autouse=True)
def clean_keys():
    auth_module._api_keys.clear()
    yield
    auth_module._api_keys.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config["TESTING"] = True
    return app.test_client()


def test_list_keys_empty(client):
    resp = client.get("/auth/keys")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["keys"] == []
    assert data["count"] == 0


def test_add_key_explicit(client):
    resp = client.post("/auth/keys", json={"key": "explicit-key-123"})
    assert resp.status_code == 201
    assert resp.get_json()["key"] == "explicit-key-123"
    assert "explicit-key-123" in auth_module._api_keys


def test_add_key_too_short(client):
    resp = client.post("/auth/keys", json={"key": "short"})
    assert resp.status_code == 400


def test_add_key_auto_generate(client):
    resp = client.post("/auth/keys", json={})
    assert resp.status_code == 201
    key = resp.get_json()["key"]
    assert key in auth_module._api_keys


def test_generate_endpoint(client):
    resp = client.post("/auth/keys/generate")
    assert resp.status_code == 201
    key = resp.get_json()["key"]
    assert key in auth_module._api_keys


def test_delete_existing_key(client):
    auth_module.add_key("deleteme")
    resp = client.delete("/auth/keys/deleteme")
    assert resp.status_code == 200
    assert "deleteme" not in auth_module._api_keys


def test_delete_nonexistent_key(client):
    resp = client.delete("/auth/keys/doesnotexist")
    assert resp.status_code == 404


def test_list_keys_after_add(client):
    auth_module.add_key("k1")
    auth_module.add_key("k2")
    resp = client.get("/auth/keys")
    data = resp.get_json()
    assert data["count"] == 2
    assert set(data["keys"]) == {"k1", "k2"}
