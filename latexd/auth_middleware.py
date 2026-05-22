"""Middleware that enforces API key auth globally on a Flask app.

When LATEXD_AUTH_MIDDLEWARE=true is set and keys are configured,
every request (except /health) must carry a valid key.
"""

import os
from flask import Flask, request, jsonify
from latexd.auth import verify_request

# Paths that are always public regardless of auth state
_PUBLIC_PATHS = {"/health", "/metrics"}


def _auth_enabled() -> bool:
    return os.environ.get("LATEXD_AUTH_MIDDLEWARE", "false").lower() == "true"


def register_auth_middleware(app: Flask) -> None:
    """Attach before-request auth enforcement to *app*."""

    @app.before_request
    def _enforce_auth():
        if not _auth_enabled():
            return None
        if request.path in _PUBLIC_PATHS:
            return None
        if not verify_request():
            return (
                jsonify(
                    {
                        "error": "Unauthorized",
                        "message": "Provide a valid API key via X-API-Key header or api_key query param.",
                    }
                ),
                401,
            )
        return None
