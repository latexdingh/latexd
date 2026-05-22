"""REST routes for managing webhooks."""

from flask import Blueprint, jsonify, request

from latexd import webhook

bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")


@bp.get("/")
def list_hooks():
    return jsonify(webhook.list_webhooks()), 200


@bp.post("/")
def register_hook():
    body = request.get_json(silent=True) or {}
    url = body.get("url", "").strip()
    if not url:
        return jsonify({"error": "'url' is required"}), 400
    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "'url' must start with http:// or https://"}), 400

    secret = body.get("secret") or None
    events = body.get("events") or None
    if events is not None and not isinstance(events, list):
        return jsonify({"error": "'events' must be a list"}), 400

    wid = webhook.register(url, secret=secret, events=events)
    return jsonify({"id": wid, "url": url}), 201


@bp.delete("/<wid>")
def delete_hook(wid: str):
    removed = webhook.unregister(wid)
    if not removed:
        return jsonify({"error": "webhook not found"}), 404
    return jsonify({"deleted": wid}), 200
