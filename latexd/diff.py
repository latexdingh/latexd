"""Snippet diff utility — compares two LaTeX snippets and returns a unified diff."""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiffResult:
    """Result of comparing two LaTeX snippets."""

    old_label: str
    new_label: str
    lines_added: int
    lines_removed: int
    unchanged: int
    unified: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "old_label": self.old_label,
            "new_label": self.new_label,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "unchanged": self.unchanged,
            "unified": self.unified,
        }


class DiffError(ValueError):
    """Raised when diffing cannot be performed."""


def diff_snippets(
    old: str,
    new: str,
    old_label: str = "old",
    new_label: str = "new",
    context: int = 3,
) -> DiffResult:
    """Return a DiffResult comparing *old* and *new* LaTeX strings.

    Args:
        old: Original LaTeX snippet.
        new: Updated LaTeX snippet.
        old_label: Label used in the unified diff header for the old version.
        new_label: Label used in the unified diff header for the new version.
        context: Number of context lines in the unified diff.

    Raises:
        DiffError: If either snippet is not a string.
    """
    if not isinstance(old, str) or not isinstance(new, str):
        raise DiffError("Both snippets must be strings.")

    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)

    unified = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=old_label,
            tofile=new_label,
            n=context,
        )
    )

    added = sum(1 for l in unified if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in unified if l.startswith("-") and not l.startswith("---"))
    unchanged = sum(1 for l in unified if l.startswith(" "))

    return DiffResult(
        old_label=old_label,
        new_label=new_label,
        lines_added=added,
        lines_removed=removed,
        unchanged=unchanged,
        unified=[l.rstrip("\n") for l in unified],
    )
