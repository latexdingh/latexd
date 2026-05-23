"""Extended edge-case tests for annotation module."""
import time
import pytest
import latexd.annotation as ann


@pytest.fixture(autouse=True)
def clean_registry():
    ann.clear()
    yield
    ann.clear()


def test_multiple_snippets_isolated():
    ann.add("sA", "note 1")
    ann.add("sB", "note 2")
    assert len(ann.list_for_snippet("sA")) == 1
    assert len(ann.list_for_snippet("sB")) == 1


def test_ids_are_unique():
    e1 = ann.add("s1", "first")
    e2 = ann.add("s1", "second")
    assert e1.id != e2.id


def test_created_at_is_recent():
    before = time.time()
    e = ann.add("s1", "timestamped")
    after = time.time()
    assert before <= e.created_at <= after


def test_remove_only_target():
    e1 = ann.add("s1", "keep me")
    e2 = ann.add("s1", "remove me")
    ann.remove(e2.id)
    remaining = ann.list_for_snippet("s1")
    assert len(remaining) == 1
    assert remaining[0].id == e1.id


def test_clear_removes_all():
    ann.add("s1", "a")
    ann.add("s2", "b")
    ann.clear()
    assert ann.list_for_snippet("s1") == []
    assert ann.list_for_snippet("s2") == []


def test_to_dict_values_match_entry():
    e = ann.add("sx", "value check", author="tester")
    d = e.to_dict()
    assert d["id"] == e.id
    assert d["snippet_id"] == "sx"
    assert d["note"] == "value check"
    assert d["author"] == "tester"
    assert d["created_at"] == e.created_at
