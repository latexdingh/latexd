"""Plugin registry for latexd — allows optional modules to register
themselves with the Flask app in a consistent, discoverable way."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import flask


@dataclass
class Plugin:
    """Descriptor for a single latexd plugin."""

    name: str
    description: str
    blueprint: flask.Blueprint
    setup: Optional[Callable[[flask.Flask], None]] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "url_prefix": self.blueprint.url_prefix or "/",
        }


# Module-level registry
_registry: List[Plugin] = []


def register(plugin: Plugin) -> None:
    """Add a plugin to the registry. Raises ValueError on duplicate name."""
    if any(p.name == plugin.name for p in _registry):
        raise ValueError(f"Plugin '{plugin.name}' is already registered.")
    _registry.append(plugin)


def unregister(name: str) -> bool:
    """Remove a plugin by name. Returns True if found and removed."""
    global _registry
    before = len(_registry)
    _registry = [p for p in _registry if p.name != name]
    return len(_registry) < before


def list_plugins() -> List[Plugin]:
    """Return a shallow copy of all registered plugins."""
    return list(_registry)


def get_plugin(name: str) -> Optional[Plugin]:
    """Look up a plugin by name."""
    return next((p for p in _registry if p.name == name), None)


def apply_all(app: flask.Flask) -> None:
    """Register every plugin's blueprint with *app* and run its setup hook."""
    for plugin in _registry:
        app.register_blueprint(plugin.blueprint)
        if plugin.setup:
            plugin.setup(app)


def clear() -> None:
    """Remove all registered plugins (primarily for testing)."""
    _registry.clear()
