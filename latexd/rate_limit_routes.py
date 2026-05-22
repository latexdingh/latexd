"""Routes for inspecting and managing the rate limiter."""

from flask import Blueprint, jsonify, request

from latexd.rate_limit import get_limiter

bp = Blueprint("rate_limit", __name__)


def _client_id() -> str:
    """Derive a client identifier from the request context."""
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")


@bp.route("/rate-limit/status", methods=["GET"])
def rate_limit_status():
    """Return the current rate-limit status for the calling client."""
    limiter = get_limiter()
    client_id = _client_id()
    remaining = limiter.remaining(client_id)
    allowed = remaining > 0
    return jsonify(
        {
            "client_id": client_id,
            "max_requests": limiter.max_requests,
            "window_seconds": limiter.window_seconds,
            "remaining": remaining,
            "allowed": allowed,
        }
    )


@bp.route("/rate-limit/reset", methods=["POST"])
def rate_limit_reset():
    """Reset rate-limit counters. Optionally pass ?client_id= to target one client."""
    limiter = get_limiter()
    target = request.args.get("client_id") or None
    limiter.reset(target)
    msg = f"Reset rate limit for '{target}'" if target else "Reset all rate limits"
    return jsonify({"message": msg})
