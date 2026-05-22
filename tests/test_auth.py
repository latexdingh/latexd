"""Unit tests for latexd.auth module."""

import pytest
from unittest.mock import patch
from flask import Flask

import latexd.auth as auth_module
from latexd.auth import (
    add_key, remove_key, generate_key, list_keys,
    verify_request, require_auth,
)


@pytest.fixture(autouse=True)
def clean_keys():
    """Ensure a clean key store for every test."""
    auth_module._api_keys.clear()
    yield
    auth_module._api_keys.clear()


@pytest.fixture()
def app():
    app = Flask(__name__)

    @app.get("/protected")
    @require_auth
    def protected():
        return "ok", 200

    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_add_and_list_key():
    add_key("abc123")
    assert "abc123" in list_keys()


def test_remove_existing_key():
    add_key("to-remove")
    result = remove_key("to-remove")
    assert result is True
    assert "to-remove" not in list_keys()


def test_remove_nonexistent_key():
    result = remove_key("ghost")
    assert result is False


def test_generate_key_registers_it():
    key = generate_key()
    assert key in list_keys()
    assert len(key) >= 16


def test_verify_request_disabled(app):
    """With no keys registered, all requests are allowed."""
    with app.test_request_context("/"):
        assert verify_request() is True


def test_verify_request_valid_header(app):
    add_key("secret")
    with app.test_request_context("/", headers={"X-API-Key": "secret"}):
        assert verify_request() is True


def test_verify_request_invalid_header(app):
    add_key("secret")
    with app.test_request_context("/", headers={"X-API-Key": "wrong"}):
        assert verify_request() is False


def test_require_auth_blocks_unauthenticated(client):
    add_key("mykey")
    resp = client.get("/protected")
    assert resp.status_code == 401


def test_require_auth_allows_valid_key(client):
    add_key("mykey")
    resp = client.get("/protected", headers={"X-API-Key": "mykey"})
    assert resp.status_code == 200


def test_require_auth_allows_when_disabled(client):
    # No keys registered => auth disabled
    resp = client.get("/protected")
    assert resp.status_code == 200
