"""Unit tests for latexd.template."""

import pytest

from latexd import template as tmpl


@pytest.fixture(autouse=True)
def clean_registry():
    tmpl.clear()
    yield
    tmpl.clear()


def test_add_returns_entry():
    entry = tmpl.add("frac", r"\frac{a}{b}", "A fraction")
    assert entry.name == "frac"
    assert entry.snippet == r"\frac{a}{b}"
    assert entry.description == "A fraction"
    assert entry.id


def test_list_shows_added():
    tmpl.add("alpha", r"\alpha")
    tmpl.add("beta", r"\beta")
    names = {e.name for e in tmpl.list_templates()}
    assert "alpha" in names
    assert "beta" in names


def test_list_returns_copy():
    tmpl.add("gamma", r"\gamma")
    lst = tmpl.list_templates()
    lst.clear()
    assert len(tmpl.list_templates()) == 1


def test_duplicate_name_raises():
    tmpl.add("dup", r"\pi")
    with pytest.raises(ValueError, match="already exists"):
        tmpl.add("dup", r"\pi")


def test_get_found():
    entry = tmpl.add("sigma", r"\sigma")
    found = tmpl.get(entry.id)
    assert found is entry


def test_get_missing_returns_none():
    assert tmpl.get("nonexistent-id") is None


def test_get_by_name_found():
    tmpl.add("omega", r"\omega")
    found = tmpl.get_by_name("omega")
    assert found is not None
    assert found.name == "omega"


def test_get_by_name_missing_returns_none():
    assert tmpl.get_by_name("nope") is None


def test_remove_existing():
    entry = tmpl.add("delta", r"\delta")
    assert tmpl.remove(entry.id) is True
    assert tmpl.get(entry.id) is None


def test_remove_missing_returns_false():
    assert tmpl.remove("no-such-id") is False


def test_to_dict_keys():
    entry = tmpl.add("phi", r"\phi", "phi symbol")
    d = entry.to_dict()
    assert set(d.keys()) == {"id", "name", "snippet", "description", "created_at"}
