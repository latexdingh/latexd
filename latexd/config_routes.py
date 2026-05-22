"""REST routes for inspecting latexd runtime configuration."""

from flask import Blueprint, jsonify, current_app

config_bp = Blueprint("config", __name__)


def get_config():
    """Retrieve the Config instance stored on the Flask app."""
    return current_app.config["LATEXD_CONFIG"]


@config_bp.route("/config", methods=["GET"])
def show_config():
    """Return the active configuration as JSON.

    Sensitive or path-specific values are included so operators can
    verify what the daemon picked up from the environment.
    """
    cfg = get_config()
    return jsonify(
        {
            "server": {
                "host": cfg.host,
                "port": cfg.port,
                "debug": cfg.debug,
            },
            "compiler": {
                "pdflatex_path": cfg.pdflatex_path,
                "inkscape_path": cfg.inkscape_path,
                "compile_timeout": cfg.compile_timeout,
            },
            "cache": {
                "enabled": cfg.cache_enabled,
                "cache_dir": cfg.cache_dir,
                "max_entries": cfg.cache_max_entries,
            },
            "latex": {
                "document_class": cfg.latex_document_class,
                "font_size": cfg.latex_font_size,
                "packages": cfg.latex_packages,
            },
        }
    )
