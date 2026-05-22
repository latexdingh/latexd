from flask import Blueprint, jsonify, request
from latexd.plugin import register, unregister, list_plugins, PluginError

plugin_routes = Blueprint("plugin_routes", __name__)


@plugin_routes.get("/plugins")
def list_all_plugins():
    """Return all registered plugins."""
    plugins = list_plugins()
    return jsonify({"plugins": [p.to_dict() for p in plugins]}), 200


@plugin_routes.post("/plugins")
def register_plugin():
    """Register a new plugin by name and entry_point."""
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    entry_point = body.get("entry_point", "").strip()
    description = body.get("description", "").strip()

    if not name:
        return jsonify({"error": "'name' is required"}), 400
    if not entry_point:
        return jsonify({"error": "'entry_point' is required"}), 400

    try:
        plugin = register(name=name, entry_point=entry_point, description=description)
    except PluginError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(plugin.to_dict()), 201


@plugin_routes.delete("/plugins/<name>")
def delete_plugin(name: str):
    """Unregister a plugin by name."""
    removed = unregister(name)
    if not removed:
        return jsonify({"error": f"Plugin '{name}' not found"}), 404
    return jsonify({"removed": name}), 200
