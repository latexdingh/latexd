"""Middleware that automatically records per-request metrics for latexd."""

import time
from flask import Flask, g, request
from latexd.metrics import get_metrics, MetricsStore


def _get_store(app: Flask) -> MetricsStore:
    return app.config.get("METRICS_STORE") or get_metrics()


def register_metrics_middleware(app: Flask) -> None:
    """Attach before/after request hooks to track metrics automatically."""

    @app.before_request
    def _before():
        g.metrics_start = time.monotonic()
        store = _get_store(app)
        store.record_request()

    @app.after_request
    def _after(response):
        start = getattr(g, "metrics_start", None)
        if start is not None:
            elapsed_ms = (time.monotonic() - start) * 1000
            fmt = request.args.get("format") or (
                request.get_json(silent=True) or {}
            ).get("format")
            if fmt and request.path == "/render":
                store = _get_store(app)
                error = response.status_code >= 400
                store.record_compilation(fmt, error=error, latency_ms=elapsed_ms)
        return response
