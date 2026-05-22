"""Request logging and timing middleware for latexd."""

import logging
import time
import uuid
from collections import deque
from threading import Lock
from typing import Callable

from flask import Flask, Request, Response, g, request

logger = logging.getLogger(__name__)

# In-memory ring buffer of recent request logs
_MAX_LOG_ENTRIES = 200
_request_log: deque = deque(maxlen=_MAX_LOG_ENTRIES)
_log_lock = Lock()


def _record(entry: dict) -> None:
    with _log_lock:
        _request_log.append(entry)


def get_request_log() -> list:
    """Return a snapshot of recent request log entries (newest last)."""
    with _log_lock:
        return list(_request_log)


def clear_request_log() -> None:
    """Clear all stored request log entries."""
    with _log_lock:
        _request_log.clear()


def register_middleware(app: Flask) -> None:
    """Attach before/after request hooks to *app*."""

    @app.before_request
    def _before() -> None:
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.perf_counter()
        logger.debug(
            "[%s] --> %s %s",
            g.request_id,
            request.method,
            request.path,
        )

    @app.after_request
    def _after(response: Response) -> Response:
        elapsed_ms = round((time.perf_counter() - g.start_time) * 1000, 2)
        request_id = getattr(g, "request_id", "-")
        entry = {
            "id": request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": elapsed_ms,
        }
        _record(entry)
        logger.info(
            "[%s] <-- %s %s %d  (%.2f ms)",
            request_id,
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Duration-Ms"] = str(elapsed_ms)
        return response
