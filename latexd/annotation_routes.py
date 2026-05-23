"""REST routes for the annotation feature."""
from flask import Blueprint, jsonify, request

import latexd.annotation as annotation_store

annotation_bp = Blueprint("annotation", __name__)


@annotation_bp.get("/annotations/<snippet_id>")
def list_annotations(snippet_id: str):
    entries = annotation_store.list_for_snippet(snippet_id)
    return jsonify([e.to_dict() for e in entries]), 200


@annotation_bp.post("/annotations/<snippet_id>")
def add_annotation(snippet_id: str):
    body = request.get_json(silent=True) or {}
    note = body.get("note", "").strip()
    author = body.get("author", "anonymous").strip() or "anonymous"
    if not note:
        return jsonify({"error": "'note' is required"}), 400
    entry = annotation_store.add(snippet_id, note, author)
    return jsonify(entry.to_dict()), 201


@annotation_bp.get("/annotations/entry/<annotation_id>")
def get_annotation(annotation_id: str):
    entry = annotation_store.get(annotation_id)
    if entry is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(entry.to_dict()), 200


@annotation_bp.delete("/annotations/entry/<annotation_id>")
def delete_annotation(annotation_id: str):
    removed = annotation_store.remove(annotation_id)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": annotation_id}), 200
