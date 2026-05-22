"""Routes for async compilation job queue."""

from flask import Blueprint, request, jsonify, Response
from .job_queue import get_queue, JobStatus
from .compiler import LatexCompiler, CompilationError
from .config import Config
import threading

bp = Blueprint("job_queue", __name__)


def _compile_in_background(job_id: str, snippet: str, fmt: str) -> None:
    queue = get_queue()
    queue.update(job_id, JobStatus.RUNNING)
    try:
        compiler = LatexCompiler(Config.from_env())
        data = compiler.compile_latex(snippet, fmt)
        queue.update(job_id, JobStatus.DONE, result=data)
    except CompilationError as exc:
        queue.update(job_id, JobStatus.FAILED, error=str(exc))
    except Exception as exc:  # pragma: no cover
        queue.update(job_id, JobStatus.FAILED, error=f"Unexpected error: {exc}")


@bp.post("/jobs")
def submit_job():
    body = request.get_json(silent=True) or {}
    snippet = body.get("snippet", "").strip()
    fmt = body.get("format", "svg").lower()

    if not snippet:
        return jsonify({"error": "'snippet' is required"}), 400
    if fmt not in ("svg", "png"):
        return jsonify({"error": "'format' must be 'svg' or 'png'"}), 400

    job = get_queue().create(snippet, fmt)
    t = threading.Thread(target=_compile_in_background,
                         args=(job.job_id, snippet, fmt), daemon=True)
    t.start()
    return jsonify(job.to_dict()), 202


@bp.get("/jobs")
def list_jobs():
    return jsonify(get_queue().all_jobs()), 200


@bp.get("/jobs/<job_id>")
def job_status(job_id: str):
    job = get_queue().get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict()), 200


@bp.get("/jobs/<job_id>/result")
def job_result(job_id: str):
    job = get_queue().get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    if job.status != JobStatus.DONE:
        return jsonify({"error": "Result not ready", "status": job.status.value}), 409
    mime = "image/svg+xml" if job.fmt == "svg" else "image/png"
    return Response(job.result, mimetype=mime)


@bp.delete("/jobs")
def clear_jobs():
    count = get_queue().clear()
    return jsonify({"cleared": count}), 200
