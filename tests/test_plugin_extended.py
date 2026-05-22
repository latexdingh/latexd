"""Extended unit tests for latexd/plugin.py covering edge cases."""
import pytest
from latexd.plugin import (
    Plugin,
    PluginError,
    _registry,
    register,
    unregister,
    list_plugins,
    get_plugin,
)


@pytest.fixture(autouse=True)
def clean_registry():
    _registry.clear()
    yield
    _registry.clear()


def test_to_dict_contains_expected_keys():
    p = Plugin(name="x", entry_point="pkg.x", description="desc")
    d = p.to_dict()
    assert set(d.keys()) >= {"name", "entry_point", "description", "registered_at"}


def test_register_returns_plugin_instance():
    p = register(name="foo", entry_point="pkg.foo")
    assert isinstance(p, Plugin)
    assert p.name == "foo"


def test_register_empty_description_defaults():
    p = register(name="bar", entry_point="pkg.bar")
    assert isinstance(p.description, str)


def test_get_plugin_found():
    register(name="baz", entry_point="pkg.baz")
    p = get_plugin("baz")
    assert p is not None
    assert p.name == "baz"


def test_get_plugin_missing_returns_none():
    result = get_plugin("nonexistent")
    assert result is None


def test_list_returns_copy():
    register(name="c1", entry_point="pkg.c1")
    lst1 = list_plugins()
    lst1.clear()
    assert len(list_plugins()) == 1


def test_unregister_missing_returns_false():
    assert unregister("missing") is False


def test_register_duplicate_raises_plugin_error():
    register(name="dup", entry_point="pkg.dup")
    with pytest.raises(PluginError):
        register(name="dup", entry_point="pkg.dup2")
