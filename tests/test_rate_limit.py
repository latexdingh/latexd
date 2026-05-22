"""Tests for the rate limiter and its routes."""

import pytest
from flask import Flask

from latexd.rate_limit import RateLimiter, get_limiter, set_limiter
from latexd.rate_limit_routes import bp


# ---------------------------------------------------------------------------
# Unit tests for RateLimiter
# ---------------------------------------------------------------------------

def test_allows_requests_within_limit():
    rl = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        assert rl.is_allowed("client-a") is True


def test_blocks_request_over_limit():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    rl.is_allowed("client-b")
    rl.is_allowed("client-b")
    assert rl.is_allowed("client-b") is False


def test_remaining_decrements():
    rl = RateLimiter(max_requests=5, window_seconds=60)
    assert rl.remaining("client-c") == 5
    rl.is_allowed("client-c")
    assert rl.remaining("client-c") == 4


def test_reset_single_client():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    rl.is_allowed("client-d")
    rl.is_allowed("client-d")
    rl.reset("client-d")
    assert rl.remaining("client-d") == 2


def test_reset_all_clients():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    rl.is_allowed("x")
    rl.is_allowed("y")
    rl.reset()
    assert rl.remaining("x") == 2
    assert rl.remaining("y") == 2


def test_clients_are_independent():
    rl = RateLimiter(max_requests=1, window_seconds=60)
    assert rl.is_allowed("alpha") is True
    assert rl.is_allowed("alpha") is False
    assert rl.is_allowed("beta") is True


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True

    isolated = RateLimiter(max_requests=10, window_seconds=60)
    set_limiter(isolated)

    with app.test_client() as c:
        yield c

    # Restore a fresh limiter after the test
    set_limiter(RateLimiter())


def test_status_returns_200(client):
    resp = client.get("/rate-limit/status")
    assert resp.status_code == 200


def test_status_payload_shape(client):
    resp = client.get("/rate-limit/status")
    data = resp.get_json()
    assert "remaining" in data
    assert "max_requests" in data
    assert "window_seconds" in data
    assert data["allowed"] is True


def test_reset_all(client):
    # Consume some quota first
    client.get("/rate-limit/status")
    resp = client.post("/rate-limit/reset")
    assert resp.status_code == 200
    assert "Reset all" in resp.get_json()["message"]


def test_reset_specific_client(client):
    resp = client.post("/rate-limit/reset?client_id=testclient")
    assert resp.status_code == 200
    assert "testclient" in resp.get_json()["message"]
