"""Tests for latexd.diff module."""

import pytest

from latexd.diff import DiffError, DiffResult, diff_snippets


SNIPPET_A = """\\documentclass{article}
\\begin{document}
Hello world
\\end{document}
"""

SNIPPET_B = """\\documentclass{article}
\\begin{document}
Hello LaTeX
\\end{document}
"""


def test_identical_snippets_produce_no_diff():
    result = diff_snippets(SNIPPET_A, SNIPPET_A)
    assert result.lines_added == 0
    assert result.lines_removed == 0
    assert result.unified == []


def test_changed_line_counts_correctly():
    result = diff_snippets(SNIPPET_A, SNIPPET_B)
    assert result.lines_added == 1
    assert result.lines_removed == 1


def test_unified_output_is_list_of_strings():
    result = diff_snippets(SNIPPET_A, SNIPPET_B)
    assert isinstance(result.unified, list)
    assert all(isinstance(l, str) for l in result.unified)


def test_unified_contains_diff_markers():
    result = diff_snippets(SNIPPET_A, SNIPPET_B)
    markers = {l[0] for l in result.unified if l and l[0] in "+-"}
    assert "+" in markers
    assert "-" in markers


def test_labels_appear_in_unified_header():
    result = diff_snippets(SNIPPET_A, SNIPPET_B, old_label="v1", new_label="v2")
    header_lines = [l for l in result.unified if l.startswith("---") or l.startswith("+++ ")]
    assert any("v1" in l for l in header_lines)
    assert any("v2" in l for l in header_lines)


def test_to_dict_contains_expected_keys():
    result = diff_snippets(SNIPPET_A, SNIPPET_B)
    d = result.to_dict()
    for key in ("old_label", "new_label", "lines_added", "lines_removed", "unchanged", "unified"):
        assert key in d


def test_to_dict_values_match_attributes():
    result = diff_snippets(SNIPPET_A, SNIPPET_B, old_label="a", new_label="b")
    d = result.to_dict()
    assert d["old_label"] == "a"
    assert d["new_label"] == "b"
    assert d["lines_added"] == result.lines_added
    assert d["lines_removed"] == result.lines_removed


def test_added_lines_only():
    old = "line1\n"
    new = "line1\nline2\n"
    result = diff_snippets(old, new)
    assert result.lines_added == 1
    assert result.lines_removed == 0


def test_removed_lines_only():
    old = "line1\nline2\n"
    new = "line1\n"
    result = diff_snippets(old, new)
    assert result.lines_added == 0
    assert result.lines_removed == 1


def test_invalid_type_raises_diff_error():
    with pytest.raises(DiffError):
        diff_snippets(None, "valid")  # type: ignore


def test_invalid_type_both_raises_diff_error():
    with pytest.raises(DiffError):
        diff_snippets(123, 456)  # type: ignore
