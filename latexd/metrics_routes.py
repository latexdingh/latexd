"""Routes for exposing and managing latexd metrics."""

from flask import Blueprint, jsonify, current_app
from latexd.metrics import get_metrics

metrics_bp = Blueprint("metrics", __name__)


def _metrics_store():
    """Return the metrics store, preferring app context override for testing."""
    return current_app.config.get("METRICS_STORE") or get_metrics()


@metrics_bp.route("/metrics", methods=["GET"])
def metrics_summary():
    """Return a summary of runtime metrics."""
    store = _metrics_store()
    return jsonify(store.to_dict()), 200


@metrics_bp.route("/metrics/reset", methods=["POST"])
def metrics_reset():
    """Reset all metrics counters."""
    store = _metrics_store()
    store.reset()
    return jsonify({"status": "ok", "message": "Metrics have been reset."}), 200
