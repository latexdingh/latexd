"""Flask routes exposing the /render endpoint."""

from flask import Blueprint, request, jsonify, Response
from .compiler import compile_latex, CompilationError

bp = Blueprint("render", __name__)

ALLOWED_FORMATS = {"svg", "png"}
MAX_SNIPPET_LEN = 8_000  # characters


@bp.post("/render")
def render():
    """Compile a LaTeX snippet to SVG or PNG.

    Request JSON body:
        snippet  (str, required)  – LaTeX source to render.
        format   (str, optional)  – ``'svg'`` (default) or ``'png'``.
        dpi      (int, optional)  – PNG resolution, default 150.

    Returns:
        SVG: ``image/svg+xml`` response.
        PNG: ``image/png`` response.
        Error: JSON with ``error`` and optional ``log`` keys.
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON."}), 400

    snippet = body.get("snippet", "")
    if not snippet or not snippet.strip():
        return jsonify({"error": "'snippet' field is required and must not be empty."}), 400
    if len(snippet) > MAX_SNIPPET_LEN:
        return jsonify({"error": f"'snippet' exceeds maximum length of {MAX_SNIPPET_LEN} characters."}), 400

    fmt = body.get("format", "svg").lower()
    if fmt not in ALLOWED_FORMATS:
        return jsonify({"error": f"'format' must be one of {sorted(ALLOWED_FORMATS)}."}), 400

    dpi = body.get("dpi", 150)
    if not isinstance(dpi, int) or not (72 <= dpi <= 600):
        return jsonify({"error": "'dpi' must be an integer between 72 and 600."}), 400

    try:
        image_bytes = compile_latex(snippet, output_format=fmt, dpi=dpi)
    except CompilationError as exc:
        payload = {"error": str(exc)}
        if exc.log:
            payload["log"] = exc.log
        return jsonify(payload), 422
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Unexpected server error: {exc}"}), 500

    mime = "image/svg+xml" if fmt == "svg" else "image/png"
    return Response(image_bytes, status=200, mimetype=mime)
