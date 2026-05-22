import pytest
from flask import Flask
from latexd.plugin_routes import plugin_routes
from latexd.plugin import _registry


@pytest.fixture(autouse=True)
def clean_registry():
    _registry.clear()
    yield
    _registry.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(plugin_routes)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_list_empty(client):
    resp = client.get("/plugins")
    assert resp.status_code == 200
    assert resp.get_json()["plugins"] == []


def test_register_plugin(client):
    resp = client.post(
        "/plugins",
        json={"name": "myplugin", "entry_point": "mypkg.myplugin", "description": "A test plugin"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "myplugin"
    assert data["entry_point"] == "mypkg.myplugin"
    assert data["description"] == "A test plugin"


def test_register_missing_name(client):
    resp = client.post("/plugins", json={"entry_point": "mypkg.myplugin"})
    assert resp.status_code == 400
    assert "name" in resp.get_json()["error"]


def test_register_missing_entry_point(client):
    resp = client.post("/plugins", json={"name": "myplugin"})
    assert resp.status_code == 400
    assert "entry_point" in resp.get_json()["error"]


def test_register_duplicate(client):
    payload = {"name": "dup", "entry_point": "pkg.dup"}
    client.post("/plugins", json=payload)
    resp = client.post("/plugins", json=payload)
    assert resp.status_code == 409


def test_delete_plugin(client):
    client.post("/plugins", json={"name": "todel", "entry_point": "pkg.todel"})
    resp = client.delete("/plugins/todel")
    assert resp.status_code == 200
    assert resp.get_json()["removed"] == "todel"


def test_delete_missing(client):
    resp = client.delete("/plugins/ghost")
    assert resp.status_code == 404


def test_list_after_register(client):
    client.post("/plugins", json={"name": "p1", "entry_point": "pkg.p1"})
    client.post("/plugins", json={"name": "p2", "entry_point": "pkg.p2"})
    resp = client.get("/plugins")
    names = [p["name"] for p in resp.get_json()["plugins"]]
    assert "p1" in names
    assert "p2" in names
