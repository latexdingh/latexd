"""REST routes for managing API keys in latexd."""

from flask import Blueprint, jsonify, request
from latexd.auth import add_key, remove_key, generate_key, list_keys, require_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/keys")
@require_auth
def list_api_keys():
    """List all registered API keys."""
    return jsonify({"keys": list_keys(), "count": len(list_keys())}), 200


@auth_bp.post("/keys")
@require_auth
def add_api_key():
    """Register a new API key supplied in the request body.

    Body JSON: {"key": "<your-key>"}
    Omit 'key' to auto-generate one.
    """
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if key:
        if not isinstance(key, str) or len(key) < 8:
            return jsonify({"error": "Key must be a string of at least 8 characters."}), 400
        add_key(key)
    else:
        key = generate_key()
    return jsonify({"key": key, "message": "Key registered."}), 201


@auth_bp.delete("/keys/<path:key>")
@require_auth
def delete_api_key(key: str):
    """Remove an API key by value."""
    removed = remove_key(key)
    if not removed:
        return jsonify({"error": "Key not found."}), 404
    return jsonify({"message": "Key removed."}), 200


@auth_bp.post("/keys/generate")
@require_auth
def generate_api_key():
    """Generate and register a new random API key."""
    key = generate_key()
    return jsonify({"key": key, "message": "New key generated and registered."}), 201
