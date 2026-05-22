import shutil
import subprocess
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


def _check_latex() -> dict:
    """Check whether pdflatex is available and executable."""
    path = shutil.which("pdflatex")
    if path is None:
        return {"status": "unavailable", "path": None}
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        version_line = result.stdout.splitlines()[0] if result.stdout else "unknown"
        return {"status": "ok", "path": path, "version": version_line}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "path": path, "error": str(exc)}


def _check_inkscape() -> dict:
    """Check whether inkscape is available (used for SVG conversion)."""
    path = shutil.which("inkscape")
    if path is None:
        return {"status": "unavailable", "path": None}
    try:
        result = subprocess.run(
            ["inkscape", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        version_line = result.stdout.splitlines()[0] if result.stdout else "unknown"
        return {"status": "ok", "path": path, "version": version_line}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "path": path, "error": str(exc)}


@health_bp.route("/health", methods=["GET"])
def health():
    """Return the overall health status of the daemon and its dependencies."""
    latex_info = _check_latex()
    inkscape_info = _check_inkscape()

    all_ok = latex_info["status"] == "ok" and inkscape_info["status"] in ("ok", "unavailable")

    payload = {
        "status": "ok" if all_ok else "degraded",
        "dependencies": {
            "pdflatex": latex_info,
            "inkscape": inkscape_info,
        },
    }
    http_status = 200 if all_ok else 503
    return jsonify(payload), http_status
