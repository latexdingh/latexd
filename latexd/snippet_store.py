"""Named snippet storage — save, retrieve, and delete reusable LaTeX snippets."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SnippetEntry:
    name: str
    body: str
    description: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "body": self.body,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


_registry: Dict[str, SnippetEntry] = {}


class DuplicateSnippetError(ValueError):
    """Raised when a snippet with the same name already exists."""


def add(name: str, body: str, description: str = "") -> SnippetEntry:
    """Register a new named snippet. Raises DuplicateSnippetError if name is taken."""
    if not name:
        raise ValueError("Snippet name must not be empty.")
    if not body:
        raise ValueError("Snippet body must not be empty.")
    if name in _registry:
        raise DuplicateSnippetError(f"Snippet '{name}' already exists.")
    entry = SnippetEntry(name=name, body=body, description=description)
    _registry[name] = entry
    return entry


def update(name: str, body: str, description: Optional[str] = None) -> SnippetEntry:
    """Update an existing snippet's body (and optionally description)."""
    if name not in _registry:
        raise KeyError(f"Snippet '{name}' not found.")
    entry = _registry[name]
    entry.body = body
    entry.updated_at = time.time()
    if description is not None:
        entry.description = description
    return entry


def remove(name: str) -> bool:
    """Delete a snippet by name. Returns True if removed, False if not found."""
    return _registry.pop(name, None) is not None


def get(name: str) -> Optional[SnippetEntry]:
    """Return the snippet entry for *name*, or None."""
    return _registry.get(name)


def list_snippets() -> List[SnippetEntry]:
    """Return a copy of all registered snippets."""
    return list(_registry.values())


def clear() -> None:
    """Remove all snippets (mainly for testing)."""
    _registry.clear()
