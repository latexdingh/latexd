"""Integration tests for job queue REST routes."""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from latexd.job_queue_routes import bp
from latexd.job_queue import get_queue, JobStatus


@pytest.fixture
def isolated_queue():
    """Reset the global queue before each test."""
    get_queue().clear()
    yield get_queue()
    get_queue().clear()


@pytest.fixture
def client(isolated_queue):
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_submit_job_missing_snippet(client):
    resp = client.post("/jobs", json={})
    assert resp.status_code == 400
    assert "snippet" in resp.get_json()["error"]


def test_submit_job_invalid_format(client):
    resp = client.post("/jobs", json={"snippet": "x", "format": "pdf"})
    assert resp.status_code == 400


def test_submit_job_accepted(client):
    with patch("latexd.job_queue_routes._compile_in_background"):
        resp = client.post("/jobs", json={"snippet": "x^2", "format": "svg"})
    assert resp.status_code == 202
    data = resp.get_json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_list_jobs_empty(client):
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_jobs_after_submit(client):
    with patch("latexd.job_queue_routes._compile_in_background"):
        client.post("/jobs", json={"snippet": "y", "format": "png"})
    resp = client.get("/jobs")
    assert len(resp.get_json()) == 1


def test_job_status_not_found(client):
    resp = client.get("/jobs/does-not-exist")
    assert resp.status_code == 404


def test_job_result_not_ready(client, isolated_queue):
    with patch("latexd.job_queue_routes._compile_in_background"):
        resp = client.post("/jobs", json={"snippet": "z", "format": "svg"})
    job_id = resp.get_json()["job_id"]
    resp2 = client.get(f"/jobs/{job_id}/result")
    assert resp2.status_code == 409


def test_job_result_done(client, isolated_queue):
    with patch("latexd.job_queue_routes._compile_in_background"):
        resp = client.post("/jobs", json={"snippet": "a", "format": "svg"})
    job_id = resp.get_json()["job_id"]
    isolated_queue.update(job_id, JobStatus.DONE, result=b"<svg/>")
    resp2 = client.get(f"/jobs/{job_id}/result")
    assert resp2.status_code == 200
    assert resp2.mimetype == "image/svg+xml"
    assert resp2.data == b"<svg/>"


def test_clear_jobs(client):
    with patch("latexd.job_queue_routes._compile_in_background"):
        client.post("/jobs", json={"snippet": "b", "format": "png"})
    resp = client.delete("/jobs")
    assert resp.status_code == 200
    assert resp.get_json()["cleared"] == 1
    assert client.get("/jobs").get_json() == []
