"""Integration tests for annotation REST routes."""
import pytest
from flask import Flask

import latexd.annotation as ann
from latexd.annotation_routes import annotation_bp


@pytest.fixture(autouse=True)
def clean_registry():
    ann.clear()
    yield
    ann.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(annotation_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_list_empty(client):
    r = client.get("/annotations/s1")
    assert r.status_code == 200
    assert r.get_json() == []


def test_add_annotation(client):
    r = client.post("/annotations/s1", json={"note": "great", "author": "bob"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["note"] == "great"
    assert data["author"] == "bob"
    assert data["snippet_id"] == "s1"


def test_add_missing_note(client):
    r = client.post("/annotations/s1", json={})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_add_blank_note(client):
    r = client.post("/annotations/s1", json={"note": "   "})
    assert r.status_code == 400


def test_get_annotation(client):
    post = client.post("/annotations/s1", json={"note": "hello"}).get_json()
    aid = post["id"]
    r = client.get(f"/annotations/entry/{aid}")
    assert r.status_code == 200
    assert r.get_json()["id"] == aid


def test_get_missing_annotation(client):
    r = client.get("/annotations/entry/ghost")
    assert r.status_code == 404


def test_delete_annotation(client):
    post = client.post("/annotations/s1", json={"note": "bye"}).get_json()
    aid = post["id"]
    r = client.delete(f"/annotations/entry/{aid}")
    assert r.status_code == 200
    assert r.get_json()["deleted"] == aid


def test_delete_missing_annotation(client):
    r = client.delete("/annotations/entry/ghost")
    assert r.status_code == 404


def test_list_after_add(client):
    client.post("/annotations/s1", json={"note": "one"})
    client.post("/annotations/s1", json={"note": "two"})
    client.post("/annotations/s2", json={"note": "other"})
    r = client.get("/annotations/s1")
    items = r.get_json()
    assert len(items) == 2
