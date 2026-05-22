"""Integration tests for /templates routes."""

import pytest
from flask import Flask

from latexd import template as tmpl
from latexd.template_routes import bp


@pytest.fixture(autouse=True)
def clean_registry():
    tmpl.clear()
    yield
    tmpl.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_list_empty(client):
    resp = client.get("/templates/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_template(client):
    resp = client.post("/templates/", json={"name": "frac", "snippet": r"\frac{a}{b}"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "frac"
    assert "id" in data


def test_create_missing_name(client):
    resp = client.post("/templates/", json={"snippet": r"\alpha"})
    assert resp.status_code == 400
    assert "name" in resp.get_json()["error"]


def test_create_missing_snippet(client):
    resp = client.post("/templates/", json={"name": "alpha"})
    assert resp.status_code == 400
    assert "snippet" in resp.get_json()["error"]


def test_create_duplicate_name(client):
    client.post("/templates/", json={"name": "dup", "snippet": r"\pi"})
    resp = client.post("/templates/", json={"name": "dup", "snippet": r"\pi"})
    assert resp.status_code == 409


def test_get_existing(client):
    r = client.post("/templates/", json={"name": "beta", "snippet": r"\beta"})
    tid = r.get_json()["id"]
    resp = client.get(f"/templates/{tid}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "beta"


def test_get_missing(client):
    resp = client.get("/templates/no-such-id")
    assert resp.status_code == 404


def test_delete_existing(client):
    r = client.post("/templates/", json={"name": "gamma", "snippet": r"\gamma"})
    tid = r.get_json()["id"]
    resp = client.delete(f"/templates/{tid}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == tid


def test_delete_missing(client):
    resp = client.delete("/templates/ghost-id")
    assert resp.status_code == 404
