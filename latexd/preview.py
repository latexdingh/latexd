"""Preview caching layer: stores rendered outputs with metadata for quick re-serving."""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PreviewEntry:
    snippet: str
    format: str
    data: bytes
    created_at: float = field(default_factory=time.time)
    hit_count: int = 0

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "size_bytes": len(self.data),
            "created_at": self.created_at,
            "hit_count": self.hit_count,
        }


class PreviewStore:
    """In-memory store for compiled preview entries."""

    def __init__(self, max_entries: int = 128) -> None:
        self._max = max_entries
        self._store: Dict[str, PreviewEntry] = {}

    def _key(self, snippet: str, fmt: str) -> str:
        import hashlib
        digest = hashlib.sha256(f"{fmt}:{snippet}".encode()).hexdigest()
        return digest

    def get(self, snippet: str, fmt: str) -> Optional[PreviewEntry]:
        entry = self._store.get(self._key(snippet, fmt))
        if entry is not None:
            entry.hit_count += 1
        return entry

    def put(self, snippet: str, fmt: str, data: bytes) -> PreviewEntry:
        if len(self._store) >= self._max:
            # Evict the least-recently created entry
            oldest = min(self._store, key=lambda k: self._store[k].created_at)
            del self._store[oldest]
        entry = PreviewEntry(snippet=snippet, format=fmt, data=data)
        self._store[self._key(snippet, fmt)] = entry
        return entry

    def remove(self, snippet: str, fmt: str) -> bool:
        key = self._key(snippet, fmt)
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def stats(self) -> dict:
        total_hits = sum(e.hit_count for e in self._store.values())
        return {
            "entries": len(self._store),
            "max_entries": self._max,
            "total_hits": total_hits,
        }


_default_store = PreviewStore()


def get_store() -> PreviewStore:
    return _default_store
