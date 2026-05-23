"""Batch compilation: submit multiple LaTeX snippets in one request."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BatchItem:
    snippet: str
    fmt: str = "svg"
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {"snippet": self.snippet, "format": self.fmt, "label": self.label}


@dataclass
class BatchResult:
    label: Optional[str]
    fmt: str
    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "format": self.fmt,
            "success": self.success,
            "data": self.data.decode() if self.data else None,
            "error": self.error,
        }


class BatchProcessor:
    """Runs a list of BatchItems through a compiler, collecting results."""

    def __init__(self, compiler) -> None:
        self._compiler = compiler

    def run(self, items: List[BatchItem]) -> List[BatchResult]:
        results: List[BatchResult] = []
        for item in items:
            try:
                data = self._compiler.compile_latex(item.snippet, item.fmt)
                results.append(
                    BatchResult(
                        label=item.label,
                        fmt=item.fmt,
                        success=True,
                        data=data,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    BatchResult(
                        label=item.label,
                        fmt=item.fmt,
                        success=False,
                        error=str(exc),
                    )
                )
        return results


def parse_batch_request(payload: dict) -> List[BatchItem]:
    """Validate and parse the JSON payload for a batch request."""
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or len(raw_items) == 0:
        raise ValueError("'items' must be a non-empty list")

    parsed: List[BatchItem] = []
    for idx, entry in enumerate(raw_items):
        if not isinstance(entry, dict):
            raise ValueError(f"Item {idx} must be an object")
        snippet = entry.get("snippet", "")
        if not snippet or not snippet.strip():
            raise ValueError(f"Item {idx} missing 'snippet'")
        fmt = entry.get("format", "svg")
        if fmt not in ("svg", "png"):
            raise ValueError(f"Item {idx} has invalid format '{fmt}'")
        parsed.append(BatchItem(snippet=snippet, fmt=fmt, label=entry.get("label")))
    return parsed
