"""Named LaTeX snippet templates that can be stored and reused."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_registry: Dict[str, "TemplateEntry"] = {}


@dataclass
class TemplateEntry:
    id: str
    name: str
    snippet: str
    description: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "snippet": self.snippet,
            "description": self.description,
            "created_at": self.created_at,
        }


def add(name: str, snippet: str, description: str = "") -> TemplateEntry:
    """Register a new template. Raises ValueError if name already exists."""
    if name in {e.name for e in _registry.values()}:
        raise ValueError(f"Template with name '{name}' already exists.")
    entry = TemplateEntry(
        id=str(uuid.uuid4()),
        name=name,
        snippet=snippet,
        description=description,
    )
    _registry[entry.id] = entry
    return entry


def remove(template_id: str) -> bool:
    """Remove a template by id. Returns True if removed, False if not found."""
    return _registry.pop(template_id, None) is not None


def get(template_id: str) -> Optional[TemplateEntry]:
    """Return a template by id, or None."""
    return _registry.get(template_id)


def get_by_name(name: str) -> Optional[TemplateEntry]:
    """Return a template by name, or None."""
    for entry in _registry.values():
        if entry.name == name:
            return entry
    return None


def list_templates() -> List[TemplateEntry]:
    """Return a copy of all registered templates."""
    return list(_registry.values())


def clear() -> None:
    """Remove all templates (primarily for testing)."""
    _registry.clear()
