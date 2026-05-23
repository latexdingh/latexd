"""Export module: bundle compiled LaTeX outputs into a zip archive."""

import io
import zipfile
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ExportEntry:
    filename: str
    data: bytes
    fmt: str

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "format": self.fmt,
            "size_bytes": len(self.data),
        }


class ExportError(Exception):
    """Raised when an export operation fails."""


def build_zip(entries: list[ExportEntry]) -> bytes:
    """Pack a list of ExportEntry objects into an in-memory ZIP archive.

    Returns the raw bytes of the ZIP file.
    Raises ExportError if *entries* is empty.
    """
    if not entries:
        raise ExportError("Cannot build an export archive with no entries.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        seen: Dict[str, int] = {}
        for entry in entries:
            name = entry.filename
            # Deduplicate filenames by appending a counter
            if name in seen:
                seen[name] += 1
                base, _, ext = name.rpartition(".")
                name = f"{base}_{seen[entry.filename]}.{ext}" if ext else f"{name}_{seen[entry.filename]}"
            else:
                seen[name] = 0
            zf.writestr(name, entry.data)
    return buf.getvalue()


def make_entry(snippet: str, fmt: str, data: bytes, index: Optional[int] = None) -> ExportEntry:
    """Create an ExportEntry with an auto-generated filename.

    Args:
        snippet: The LaTeX snippet (used only for naming).
        fmt: Output format, e.g. ``'svg'`` or ``'png'``.
        data: Compiled binary payload.
        index: Optional numeric suffix to disambiguate filenames.
    """
    label = snippet.strip().split()[0].lstrip("\\") if snippet.strip() else "output"
    label = "".join(c for c in label if c.isalnum() or c in "-_")[:32] or "output"
    suffix = f"_{index}" if index is not None else ""
    filename = f"{label}{suffix}.{fmt}"
    return ExportEntry(filename=filename, data=data, fmt=fmt)
