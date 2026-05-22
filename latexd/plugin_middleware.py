"""Middleware that attaches plugin-count metadata to every response."""
from flask import Flask, g
from latexd.plugin import list_plugins


def _plugin_count() -> int:
    return len(list_plugins())


def register_plugin_middleware(app: Flask) -> None:
    """Register before/after hooks that expose plugin stats in response headers."""

    @app.before_request
    def _before():
        g.plugin_count = _plugin_count()

    @app.after_request
    def _after(response):
        count = getattr(g, "plugin_count", _plugin_count())
        response.headers["X-Plugin-Count"] = str(count)
        return response
