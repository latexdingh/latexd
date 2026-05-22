"""Unit tests for RenderCache."""

import pytest

from latexd.cache import RenderCache


@pytest.fixture
def cache(tmp_path):
    return RenderCache(cache_dir=tmp_path)


def test_get_miss(cache):
    assert cache.get("x^2", "svg") is None


def test_set_and_get(cache):
    data = b"<svg>...</svg>"
    cache.set("x^2", "svg", data)
    assert cache.get("x^2", "svg") == data


def test_different_formats_are_independent(cache):
    cache.set("x^2", "svg", b"svg-data")
    cache.set("x^2", "png", b"png-data")
    assert cache.get("x^2", "svg") == b"svg-data"
    assert cache.get("x^2", "png") == b"png-data"


def test_different_snippets_are_independent(cache):
    cache.set("a", "svg", b"aaa")
    cache.set("b", "svg", b"bbb")
    assert cache.get("a", "svg") == b"aaa"
    assert cache.get("b", "svg") == b"bbb"


def test_invalidate_existing(cache):
    cache.set("x^2", "svg", b"data")
    assert cache.invalidate("x^2", "svg") is True
    assert cache.get("x^2", "svg") is None


def test_invalidate_missing(cache):
    assert cache.invalidate("nonexistent", "svg") is False


def test_clear(cache):
    cache.set("a", "svg", b"1")
    cache.set("b", "png", b"2")
    cache.set("c", "svg", b"3")
    removed = cache.clear()
    assert removed == 3
    assert cache.size == 0


def test_size(cache):
    assert cache.size == 0
    cache.set("a", "svg", b"1")
    cache.set("b", "png", b"2")
    assert cache.size == 2
