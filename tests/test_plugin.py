"""Tests for latexd/plugin.py"""

import pytest
import flask

from latexd import plugin as plugin_mod
from latexd.plugin import Plugin, register, unregister, list_plugins, get_plugin, apply_all, clear


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure a clean plugin registry before and after every test."""
    clear()
    yield
    clear()


def _make_plugin(name: str, prefix: str = "/test") -> Plugin:
    bp = flask.Blueprint(name, __name__, url_prefix=prefix)
    return Plugin(name=name, description=f"Plugin {name}", blueprint=bp)


# ---------------------------------------------------------------------------
# register / list
# ---------------------------------------------------------------------------

def test_register_adds_plugin():
    p = _make_plugin("alpha")
    register(p)
    assert len(list_plugins()) == 1
    assert list_plugins()[0].name == "alpha"


def test_register_duplicate_raises():
    register(_make_plugin("alpha"))
    with pytest.raises(ValueError, match="already registered"):
        register(_make_plugin("alpha"))


def test_list_returns_copy():
    register(_make_plugin("alpha"))
    lst = list_plugins()
    lst.clear()
    assert len(list_plugins()) == 1  # original registry unaffected


# ---------------------------------------------------------------------------
# get_plugin
# ---------------------------------------------------------------------------

def test_get_existing_plugin():
    register(_make_plugin("beta"))
    p = get_plugin("beta")
    assert p is not None
    assert p.name == "beta"


def test_get_missing_plugin_returns_none():
    assert get_plugin("nonexistent") is None


# ---------------------------------------------------------------------------
# unregister
# ---------------------------------------------------------------------------

def test_unregister_removes_plugin():
    register(_make_plugin("gamma"))
    result = unregister("gamma")
    assert result is True
    assert get_plugin("gamma") is None


def test_unregister_missing_returns_false():
    assert unregister("ghost") is False


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------

def test_to_dict_shape():
    p = _make_plugin("delta", prefix="/delta")
    d = p.to_dict()
    assert d["name"] == "delta"
    assert d["url_prefix"] == "/delta"
    assert "description" in d


# ---------------------------------------------------------------------------
# apply_all
# ---------------------------------------------------------------------------

def test_apply_all_registers_blueprints():
    setup_called = []

    bp = flask.Blueprint("epsilon", __name__, url_prefix="/eps")

    @bp.route("/ping")
    def ping():
        return "pong"

    p = Plugin(
        name="epsilon",
        description="test plugin",
        blueprint=bp,
        setup=lambda app: setup_called.append(True),
    )
    register(p)

    app = flask.Flask(__name__)
    apply_all(app)

    assert setup_called == [True]
    with app.test_client() as c:
        resp = c.get("/eps/ping")
        assert resp.status_code == 200
