import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from latexd.health import health_bp


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _make_run_result(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    return result


def test_health_all_ok(client):
    with patch("latexd.health.shutil.which", return_value="/usr/bin/pdflatex"), \
         patch("latexd.health.subprocess.run", return_value=_make_run_result("pdfTeX 3.141\n")):
        resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["dependencies"]["pdflatex"]["status"] == "ok"


def test_health_pdflatex_missing(client):
    def which_side_effect(cmd):
        return None if cmd == "pdflatex" else "/usr/bin/inkscape"

    with patch("latexd.health.shutil.which", side_effect=which_side_effect), \
         patch("latexd.health.subprocess.run", return_value=_make_run_result("Inkscape 1.2\n")):
        resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["status"] == "degraded"
    assert data["dependencies"]["pdflatex"]["status"] == "unavailable"


def test_health_inkscape_missing_is_ok(client):
    def which_side_effect(cmd):
        return "/usr/bin/pdflatex" if cmd == "pdflatex" else None

    with patch("latexd.health.shutil.which", side_effect=which_side_effect), \
         patch("latexd.health.subprocess.run", return_value=_make_run_result("pdfTeX 3.141\n")):
        resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["dependencies"]["inkscape"]["status"] == "unavailable"


def test_health_pdflatex_subprocess_error(client):
    with patch("latexd.health.shutil.which", return_value="/usr/bin/pdflatex"), \
         patch("latexd.health.subprocess.run", side_effect=OSError("exec failed")):
        resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["dependencies"]["pdflatex"]["status"] == "error"
    assert "exec failed" in data["dependencies"]["pdflatex"]["error"]


def test_health_response_shape(client):
    with patch("latexd.health.shutil.which", return_value="/usr/bin/pdflatex"), \
         patch("latexd.health.subprocess.run", return_value=_make_run_result("pdfTeX 3.141\n")):
        resp = client.get("/health")
    data = resp.get_json()
    assert "status" in data
    assert "dependencies" in data
    assert "pdflatex" in data["dependencies"]
    assert "inkscape" in data["dependencies"]
