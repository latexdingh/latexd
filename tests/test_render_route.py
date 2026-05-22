"""Tests for the /render endpoint (routes + compiler integration, mocked)."""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from latexd.routes import bp
from latexd.compiler import CompilationError


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


SVG_BYTES = b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"
PNG_BYTES = b"\x89PNG\r\n\x1a\n"


def test_render_svg_success(client):
    with patch("latexd.routes.compile_latex", return_value=SVG_BYTES) as mock_compile:
        resp = client.post("/render", json={"snippet": r"$E=mc^2$"})
    assert resp.status_code == 200
    assert resp.content_type == "image/svg+xml"
    assert resp.data == SVG_BYTES
    mock_compile.assert_called_once_with(r"$E=mc^2$", output_format="svg", dpi=150)


def test_render_png_success(client):
    with patch("latexd.routes.compile_latex", return_value=PNG_BYTES):
        resp = client.post("/render", json={"snippet": r"$x^2$", "format": "png", "dpi": 200})
    assert resp.status_code == 200
    assert resp.content_type == "image/png"


def test_render_missing_snippet(client):
    resp = client.post("/render", json={})
    assert resp.status_code == 400
    assert "snippet" in resp.get_json()["error"]


def test_render_invalid_format(client):
    resp = client.post("/render", json={"snippet": r"$x$", "format": "pdf"})
    assert resp.status_code == 400


def test_render_invalid_dpi(client):
    resp = client.post("/render", json={"snippet": r"$x$", "dpi": 9999})
    assert resp.status_code == 400


def test_render_compilation_error_returns_422(client):
    with patch("latexd.routes.compile_latex", side_effect=CompilationError("bad tex", log="! Error")):
        resp = client.post("/render", json={"snippet": r"\badinput"})
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["error"] == "bad tex"
    assert body["log"] == "! Error"


def test_render_snippet_too_long(client):
    resp = client.post("/render", json={"snippet": "x" * 9000})
    assert resp.status_code == 400


def test_render_non_json_body(client):
    resp = client.post("/render", data="not json", content_type="text/plain")
    assert resp.status_code == 400
