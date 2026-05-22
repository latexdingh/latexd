"""REST routes for the named-snippet store."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

import latexd.snippet_store as store
from latexd.snippet_store import DuplicateSnippetError

snippet_bp = Blueprint("snippets", __name__, url_prefix="/snippets")


@snippet_bp.get("/")
def list_all_snippets():
    return jsonify([s.to_dict() for s in store.list_snippets()]), 200


@snippet_bp.post("/")
def create_snippet():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    body = data.get("body", "").strip()
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "'name' is required"}), 400
    if not body:
        return jsonify({"error": "'body' is required"}), 400

    try:
        entry = store.add(name, body, description)
    except DuplicateSnippetError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(entry.to_dict()), 201


@snippet_bp.get("/<name>")
def get_snippet(name: str):
    entry = store.get(name)
    if entry is None:
        return jsonify({"error": f"Snippet '{name}' not found"}), 404
    return jsonify(entry.to_dict()), 200


@snippet_bp.put("/<name>")
def update_snippet(name: str):
    data = request.get_json(silent=True) or {}
    body = data.get("body", "").strip()
    description = data.get("description")  # None means "don't change"

    if not body:
        return jsonify({"error": "'body' is required"}), 400

    try:
        entry = store.update(name, body, description)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify(entry.to_dict()), 200


@snippet_bp.delete("/<name>")
def delete_snippet(name: str):
    removed = store.remove(name)
    if not removed:
        return jsonify({"error": f"Snippet '{name}' not found"}), 404
    return "", 204
