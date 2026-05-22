"""REST routes for cache management."""

from flask import Blueprint, jsonify, request

from latexd.cache import RenderCache

cache_bp = Blueprint("cache", __name__, url_prefix="/cache")
_cache = RenderCache()


@cache_bp.route("/stats", methods=["GET"])
def cache_stats():
    """Return basic cache statistics."""
    return jsonify({"entries": _cache.size, "cache_dir": str(_cache.cache_dir)})


@cache_bp.route("/clear", methods=["DELETE"])
def cache_clear():
    """Remove all cached render results."""
    removed = _cache.clear()
    return jsonify({"removed": removed})


@cache_bp.route("/entry", methods=["DELETE"])
def cache_invalidate():
    """Invalidate a single cache entry.

    Expects JSON body: {"snippet": "...", "format": "svg|png"}
    """
    body = request.get_json(silent=True) or {}
    snippet = body.get("snippet", "")
    fmt = body.get("format", "svg").lower()

    if not snippet:
        return jsonify({"error": "'snippet' is required"}), 400
    if fmt not in ("svg", "png"):
        return jsonify({"error": "'format' must be 'svg' or 'png'"}), 400

    existed = _cache.invalidate(snippet, fmt)
    return jsonify({"invalidated": existed})


def get_cache() -> RenderCache:
    """Expose the module-level cache instance for use in other modules."""
    return _cache
