"""REST routes for managing LaTeX snippet templates."""

from flask import Blueprint, jsonify, request

from latexd import template as tmpl

bp = Blueprint("template", __name__, url_prefix="/templates")


@bp.get("/")
def list_all_templates():
    return jsonify([t.to_dict() for t in tmpl.list_templates()]), 200


@bp.post("/")
def create_template():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    snippet = data.get("snippet", "").strip()
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "'name' is required"}), 400
    if not snippet:
        return jsonify({"error": "'snippet' is required"}), 400

    try:
        entry = tmpl.add(name, snippet, description)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(entry.to_dict()), 201


@bp.get("/<template_id>")
def get_template(template_id: str):
    entry = tmpl.get(template_id)
    if entry is None:
        return jsonify({"error": "template not found"}), 404
    return jsonify(entry.to_dict()), 200


@bp.delete("/<template_id>")
def delete_template(template_id: str):
    removed = tmpl.remove(template_id)
    if not removed:
        return jsonify({"error": "template not found"}), 404
    return jsonify({"deleted": template_id}), 200
