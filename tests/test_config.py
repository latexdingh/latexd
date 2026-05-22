"""Tests for Config dataclass and /config route."""

import pytest
from flask import Flask

from latexd.config import Config
from latexd.config_routes import config_bp


# ---------------------------------------------------------------------------
# Config unit tests
# ---------------------------------------------------------------------------


def test_defaults():
    cfg = Config()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 5000
    assert cfg.debug is False
    assert cfg.compile_timeout == 30
    assert cfg.cache_enabled is True
    assert cfg.cache_max_entries == 256
    assert "amsmath" in cfg.latex_packages


def test_from_env_overrides(monkeypatch):
    monkeypatch.setenv("LATEXD_HOST", "0.0.0.0")
    monkeypatch.setenv("LATEXD_PORT", "8080")
    monkeypatch.setenv("LATEXD_DEBUG", "true")
    monkeypatch.setenv("LATEXD_TIMEOUT", "60")
    monkeypatch.setenv("LATEXD_CACHE_ENABLED", "false")
    monkeypatch.setenv("LATEXD_CACHE_MAX", "512")
    monkeypatch.setenv("LATEXD_CACHE_DIR", "/tmp/latexd_cache")
    monkeypatch.setenv("LATEXD_FONT_SIZE", "11pt")
    monkeypatch.setenv("LATEXD_DOCUMENT_CLASS", "article")

    cfg = Config.from_env()

    assert cfg.host == "0.0.0.0"
    assert cfg.port == 8080
    assert cfg.debug is True
    assert cfg.compile_timeout == 60
    assert cfg.cache_enabled is False
    assert cfg.cache_max_entries == 512
    assert cfg.cache_dir == "/tmp/latexd_cache"
    assert cfg.latex_font_size == "11pt"
    assert cfg.latex_document_class == "article"


def test_from_env_cache_dir_empty_string(monkeypatch):
    monkeypatch.setenv("LATEXD_CACHE_DIR", "")
    cfg = Config.from_env()
    assert cfg.cache_dir is None


def test_latex_packages_str():
    cfg = Config(latex_packages=["amsmath", "amssymb"])
    result = cfg.latex_packages_str()
    assert result == "\\usepackage{amsmath}\n\\usepackage{amssymb}"


def test_latex_packages_str_empty():
    """latex_packages_str() should return an empty string when no packages are set."""
    cfg = Config(latex_packages=[])
    assert cfg.latex_packages_str() == ""


# ---------------------------------------------------------------------------
# /config route tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.config["LATEXD_CONFIG"] = Config(
        host="127.0.0.1",
        port=5000,
        debug=False,
        cache_enabled=True,
        cache_max_entries=128,
        latex_packages=["amsmath"],
    )
    app.register_blueprint(config_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_config_route_returns_200(client):
    resp = client.get("/config")
    assert resp.status_code == 200


def test_config_route_structure(client):
    data = client.get("/config").get_json()
    assert "server" in data
    assert "compiler" in data
    assert "cache" in data
    assert "latex" in data


def test_config_route_values(client):
    data = client.get("/config").get_json()
    assert data["server"]["port"] == 5000
    assert data["cache"]["max_entries"] == 128
    assert "amsmath" in data["latex"]["packages"]


def test_config_route_content_type(client):
    """The /config endpoint should respond with JSON content type."""
    resp = client.get("/config")
    assert resp.content_type == "application/json"
