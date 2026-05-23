"""Tests for latexd/batch.py"""
import pytest

from latexd.batch import BatchItem, BatchProcessor, parse_batch_request
from latexd.compiler import CompilationError


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------

class _OkCompiler:
    """Always returns a fixed bytes payload."""
    def compile_latex(self, snippet: str, fmt: str) -> bytes:
        return f"<output fmt={fmt}>".encode()


class _FailCompiler:
    """Always raises CompilationError."""
    def compile_latex(self, snippet: str, fmt: str) -> bytes:
        raise CompilationError("pdflatex failed")


class _SelectiveCompiler:
    """Fails for snippets containing 'bad'."""
    def compile_latex(self, snippet: str, fmt: str) -> bytes:
        if "bad" in snippet:
            raise CompilationError("bad snippet")
        return b"<ok>"


# ---------------------------------------------------------------------------
# parse_batch_request
# ---------------------------------------------------------------------------

def test_parse_valid_items():
    payload = {
        "items": [
            {"snippet": r"$x^2$", "format": "svg"},
            {"snippet": r"$y$", "format": "png", "label": "eqn2"},
        ]
    }
    items = parse_batch_request(payload)
    assert len(items) == 2
    assert items[0].fmt == "svg"
    assert items[1].label == "eqn2"


def test_parse_default_format():
    payload = {"items": [{"snippet": r"$a$"}]}
    items = parse_batch_request(payload)
    assert items[0].fmt == "svg"


def test_parse_missing_items_key():
    with pytest.raises(ValueError, match="'items'"):
        parse_batch_request({})


def test_parse_empty_items_list():
    with pytest.raises(ValueError, match="non-empty"):
        parse_batch_request({"items": []})


def test_parse_missing_snippet():
    with pytest.raises(ValueError, match="missing 'snippet'"):
        parse_batch_request({"items": [{"format": "svg"}]})


def test_parse_invalid_format():
    with pytest.raises(ValueError, match="invalid format"):
        parse_batch_request({"items": [{"snippet": r"$x$", "format": "pdf"}]})


# ---------------------------------------------------------------------------
# BatchProcessor
# ---------------------------------------------------------------------------

def test_run_all_success():
    items = [BatchItem(snippet=r"$x$", fmt="svg", label="a"),
             BatchItem(snippet=r"$y$", fmt="png", label="b")]
    results = BatchProcessor(_OkCompiler()).run(items)
    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].data == b"<output fmt=svg>"


def test_run_all_fail():
    items = [BatchItem(snippet=r"$x$", fmt="svg")]
    results = BatchProcessor(_FailCompiler()).run(items)
    assert results[0].success is False
    assert "pdflatex failed" in results[0].error


def test_run_partial_failure():
    items = [
        BatchItem(snippet="good", fmt="svg", label="ok"),
        BatchItem(snippet="bad", fmt="svg", label="fail"),
    ]
    results = BatchProcessor(_SelectiveCompiler()).run(items)
    assert results[0].success is True
    assert results[1].success is False


def test_to_dict_success():
    items = [BatchItem(snippet=r"$x$", fmt="svg", label="lbl")]
    result = BatchProcessor(_OkCompiler()).run(items)[0]
    d = result.to_dict()
    assert d["success"] is True
    assert d["label"] == "lbl"
    assert d["error"] is None


def test_to_dict_failure():
    items = [BatchItem(snippet=r"$x$", fmt="png")]
    result = BatchProcessor(_FailCompiler()).run(items)[0]
    d = result.to_dict()
    assert d["success"] is False
    assert d["data"] is None
