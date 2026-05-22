"""Simple API key authentication for latexd."""

import os
import secrets
from functools import wraps
from flask import request, jsonify

# In-memory set of valid API keys (loaded from env or generated)
_api_keys: set[str] = set()


def _load_keys() -> None:
    """Load API keys from environment variable LATEXD_API_KEYS (comma-separated)."""
    raw = os.environ.get("LATEXD_API_KEYS", "")
    if raw.strip():
        for key in raw.split(","):
            key = key.strip()
            if key:
                _api_keys.add(key)


def _is_enabled() -> bool:
    """Return True if auth is enabled (at least one key is configured)."""
    return bool(_api_keys)


def add_key(key: str) -> None:
    """Register a new API key at runtime."""
    _api_keys.add(key)


def remove_key(key: str) -> bool:
    """Remove an API key. Returns True if it existed."""
    if key in _api_keys:
        _api_keys.discard(key)
        return True
    return False


def generate_key() -> str:
    """Generate a cryptographically secure API key and register it."""
    key = secrets.token_urlsafe(32)
    _api_keys.add(key)
    return key


def list_keys() -> list[str]:
    """Return a copy of all registered keys."""
    return list(_api_keys)


def verify_request() -> bool:
    """Check the current request carries a valid API key.

    Accepts key via:
      - Header:  X-API-Key: <key>
      - Query:   ?api_key=<key>
    """
    if not _is_enabled():
        return True  # auth disabled — allow all
    key = request.headers.get("X-API-Key") or request.args.get("api_key", "")
    return key in _api_keys


def require_auth(fn):
    """Decorator that enforces API key authentication on a route."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not verify_request():
            return jsonify({"error": "Unauthorized", "message": "Valid API key required."}), 401
        return fn(*args, **kwargs)
    return wrapper


# Load keys at import time
_load_keys()
