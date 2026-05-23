"""Annotation store: attach named metadata notes to compiled snippets."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnnotationEntry:
    id: str
    snippet_id: str
    note: str
    author: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "snippet_id": self.snippet_id,
            "note": self.note,
            "author": self.author,
            "created_at": self.created_at,
        }


class AnnotationNotFoundError(KeyError):
    """Raised when an annotation does not exist."""


_registry: Dict[str, AnnotationEntry] = {}


def add(snippet_id: str, note: str, author: str = "anonymous") -> AnnotationEntry:
    """Create and store a new annotation."""
    if not note.strip():
        raise ValueError("note must not be empty")
    entry = AnnotationEntry(
        id=str(uuid.uuid4()),
        snippet_id=snippet_id,
        note=note,
        author=author,
    )
    _registry[entry.id] = entry
    return entry


def get(annotation_id: str) -> Optional[AnnotationEntry]:
    """Return annotation by id, or None."""
    return _registry.get(annotation_id)


def list_for_snippet(snippet_id: str) -> List[AnnotationEntry]:
    """Return all annotations attached to a snippet."""
    return [e for e in _registry.values() if e.snippet_id == snippet_id]


def remove(annotation_id: str) -> bool:
    """Delete an annotation; return True if it existed."""
    return _registry.pop(annotation_id, None) is not None


def clear() -> None:
    """Remove all annotations (used in tests)."""
    _registry.clear()
