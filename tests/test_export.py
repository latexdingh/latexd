"""Tests for latexd/export.py."""

import zipfile
import io
import pytest

from latexd.export import ExportEntry, ExportError, build_zip, make_entry


# ---------------------------------------------------------------------------
# ExportEntry
# ---------------------------------------------------------------------------

def test_to_dict_contains_expected_keys():
    entry = ExportEntry(filename="out.svg", data=b"<svg/>", fmt="svg")
    d = entry.to_dict()
    assert d["filename"] == "out.svg"
    assert d["format"] == "svg"
    assert d["size_bytes"] == len(b"<svg/>")


# ---------------------------------------------------------------------------
# build_zip
# ---------------------------------------------------------------------------

def test_build_zip_empty_raises():
    with pytest.raises(ExportError, match="no entries"):
        build_zip([])


def test_build_zip_single_entry():
    entry = ExportEntry(filename="formula.svg", data=b"<svg/>", fmt="svg")
    raw = build_zip([entry])
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
    assert "formula.svg" in names


def test_build_zip_multiple_entries():
    entries = [
        ExportEntry(filename="a.png", data=b"PNG1", fmt="png"),
        ExportEntry(filename="b.png", data=b"PNG2", fmt="png"),
    ]
    raw = build_zip(entries)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        assert set(zf.namelist()) == {"a.png", "b.png"}


def test_build_zip_deduplicates_filenames():
    entries = [
        ExportEntry(filename="out.svg", data=b"first", fmt="svg"),
        ExportEntry(filename="out.svg", data=b"second", fmt="svg"),
    ]
    raw = build_zip(entries)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
    assert len(names) == 2
    assert "out.svg" in names
    # second entry should have been renamed
    assert any(n != "out.svg" for n in names)


def test_build_zip_data_is_preserved():
    payload = b"<svg>hello</svg>"
    entry = ExportEntry(filename="x.svg", data=payload, fmt="svg")
    raw = build_zip([entry])
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        assert zf.read("x.svg") == payload


# ---------------------------------------------------------------------------
# make_entry
# ---------------------------------------------------------------------------

def test_make_entry_filename_uses_fmt():
    entry = make_entry(r"\frac{1}{2}", "svg", b"<svg/>")
    assert entry.filename.endswith(".svg")


def test_make_entry_with_index():
    entry = make_entry(r"\alpha", "png", b"PNG", index=3)
    assert "_3" in entry.filename
    assert entry.filename.endswith(".png")


def test_make_entry_empty_snippet_defaults():
    entry = make_entry("", "svg", b"<svg/>")
    assert entry.filename.startswith("output")


def test_make_entry_stores_data_and_fmt():
    data = b"data"
    entry = make_entry("x", "png", data)
    assert entry.data == data
    assert entry.fmt == "png"
