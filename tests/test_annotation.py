"""Unit tests for latexd.annotation."""
import pytest
import latexd.annotation as ann


@pytest.fixture(autouse=True)
def clean_registry():
    ann.clear()
    yield
    ann.clear()


def test_add_returns_entry():
    e = ann.add("s1", "looks good")
    assert e.snippet_id == "s1"
    assert e.note == "looks good"
    assert e.author == "anonymous"
    assert e.id


def test_add_custom_author():
    e = ann.add("s1", "nice", author="alice")
    assert e.author == "alice"


def test_add_empty_note_raises():
    with pytest.raises(ValueError):
        ann.add("s1", "   ")


def test_get_existing():
    e = ann.add("s1", "hello")
    fetched = ann.get(e.id)
    assert fetched is e


def test_get_missing_returns_none():
    assert ann.get("nonexistent") is None


def test_list_for_snippet_returns_only_matching():
    ann.add("s1", "note A")
    ann.add("s1", "note B")
    ann.add("s2", "note C")
    results = ann.list_for_snippet("s1")
    assert len(results) == 2
    assert all(e.snippet_id == "s1" for e in results)


def test_list_for_snippet_empty():
    assert ann.list_for_snippet("unknown") == []


def test_remove_existing_returns_true():
    e = ann.add("s1", "to remove")
    assert ann.remove(e.id) is True
    assert ann.get(e.id) is None


def test_remove_missing_returns_false():
    assert ann.remove("ghost") is False


def test_to_dict_contains_expected_keys():
    e = ann.add("s1", "check keys")
    d = e.to_dict()
    for key in ("id", "snippet_id", "note", "author", "created_at"):
        assert key in d
