"""Simple file-based cache for compiled LaTeX outputs."""

import hashlib
import os
from pathlib import Path

DEFAULT_CACHE_DIR = Path(os.environ.get("LATEXD_CACHE_DIR", "/tmp/latexd_cache"))


class RenderCache:
    """Disk-backed cache keyed by (snippet, format) hash."""

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, snippet: str, fmt: str) -> str:
        payload = f"{fmt}:{snippet}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def _path(self, snippet: str, fmt: str) -> Path:
        ext = fmt.lower()
        return self.cache_dir / f"{self._key(snippet, fmt)}.{ext}"

    def get(self, snippet: str, fmt: str) -> bytes | None:
        """Return cached bytes or None if not cached."""
        p = self._path(snippet, fmt)
        if p.exists():
            return p.read_bytes()
        return None

    def set(self, snippet: str, fmt: str, data: bytes) -> None:
        """Store compiled output in cache."""
        p = self._path(snippet, fmt)
        p.write_bytes(data)

    def invalidate(self, snippet: str, fmt: str) -> bool:
        """Remove a cached entry. Returns True if it existed."""
        p = self._path(snippet, fmt)
        if p.exists():
            p.unlink()
            return True
        return False

    def clear(self) -> int:
        """Remove all cached entries. Returns count of removed files."""
        removed = 0
        for f in self.cache_dir.glob("*.svg"):
            f.unlink()
            removed += 1
        for f in self.cache_dir.glob("*.png"):
            f.unlink()
            removed += 1
        return removed

    @property
    def size(self) -> int:
        """Return number of cached entries."""
        return len(list(self.cache_dir.glob("*.svg"))) + len(
            list(self.cache_dir.glob("*.png"))
        )
