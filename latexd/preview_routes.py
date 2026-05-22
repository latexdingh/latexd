"""Routes for managing and inspecting the preview store."""

from flask import Blueprint, jsonify, request
from latexd.preview import PreviewStore

preview_bp = Blueprint("preview", __name__)

_store: PreviewStore | None = None


def get_preview_store() -> PreviewStore:
    from latexd.preview import get_store
    return _store if _store is not None else get_store()


@preview_bp.route("/preview/stats", methods=["GET"])
def preview_stats():
    """Return statistics about the current preview store."""
    return jsonify(get_preview_store().stats()), 200


@preview_bp.route("/preview/clear", methods=["POST"])
def preview_clear():
    """Evict all entries from the preview store."""
    removed = get_preview_store().clear()
    return jsonify({"cleared": removed}), 200


@preview_bp.route("/preview/invalidate", methods=["POST"])
def preview_invalidate():
    """Invalidate a single entry identified by snippet + format."""
    body = request.get_json(silent=True) or {}
    snippet = body.get("snippet", "")
    fmt = body.get("format", "svg")
    if not snippet:
        return jsonify({"error": "'snippet' is required"}), 400
    removed = get_preview_store().remove(snippet, fmt)
    return jsonify({"removed": removed}), 200
