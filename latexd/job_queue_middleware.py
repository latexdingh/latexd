"""Middleware that attaches job queue stats to response headers."""

from flask import Flask, g
from .job_queue import get_queue, JobStatus


def _pending_count() -> int:
    return sum(
        1 for j in get_queue()._jobs.values()
        if j.status in (JobStatus.PENDING, JobStatus.RUNNING)
    )


def register_job_queue_middleware(app: Flask) -> None:
    """Attach job-queue headers to every response."""

    @app.after_request
    def _attach_queue_headers(response):
        try:
            total = len(get_queue()._jobs)
            pending = _pending_count()
            response.headers["X-Queue-Total"] = str(total)
            response.headers["X-Queue-Pending"] = str(pending)
        except Exception:  # pragma: no cover
            pass
        return response
