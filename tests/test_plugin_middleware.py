import pytest
from flask import Flask
from latexd.plugin_middleware import register_plugin_middleware
from latexd.plugin import register, _registry


@pytest.fixture(autouse=True)
def clean_registry():
    _registry.clear()
    yield
    _registry.clear()


@pytest.fixture()
def app():
    application = Flask(__name__)
    register_plugin_middleware(application)

    @application.get("/ping")
    def ping():
        return "pong", 200

    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c


def test_header_present_when_no_plugins(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.headers.get("X-Plugin-Count") == "0"


def test_header_reflects_registered_plugins(client):
    register(name="alpha", entry_point="pkg.alpha")
    register(name="beta", entry_point="pkg.beta")
    resp = client.get("/ping")
    assert resp.headers.get("X-Plugin-Count") == "2"


def test_header_after_unregister(client):
    from latexd.plugin import unregister
    register(name="gamma", entry_point="pkg.gamma")
    unregister("gamma")
    resp = client.get("/ping")
    assert resp.headers.get("X-Plugin-Count") == "0"
