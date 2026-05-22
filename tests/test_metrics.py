"""Unit tests for latexd.metrics module."""

import time
import pytest
from latexd.metrics import MetricsStore


@pytest.fixture
def store():
    return MetricsStore()


def test_initial_state(store):
    d = store.to_dict()
    assert d["total_requests"] == 0
    assert d["total_compilations"] == 0
    assert d["compilation_errors"] == 0
    assert d["cache_hits"] == 0
    assert d["cache_misses"] == 0
    assert d["format_counts"] == {}
    assert d["avg_latency_ms"] == 0.0


def test_record_request(store):
    store.record_request()
    store.record_request()
    assert store.to_dict()["total_requests"] == 2


def test_record_compilation_success(store):
    store.record_compilation("svg", error=False, latency_ms=42.5)
    d = store.to_dict()
    assert d["total_compilations"] == 1
    assert d["compilation_errors"] == 0
    assert d["format_counts"] == {"svg": 1}
    assert d["avg_latency_ms"] == 42.5


def test_record_compilation_error(store):
    store.record_compilation("png", error=True, latency_ms=10.0)
    d = store.to_dict()
    assert d["compilation_errors"] == 1
    assert d["format_counts"] == {"png": 1}


def test_multiple_formats(store):
    store.record_compilation("svg")
    store.record_compilation("svg")
    store.record_compilation("png")
    assert store.to_dict()["format_counts"] == {"svg": 2, "png": 1}


def test_cache_tracking(store):
    store.record_cache_hit()
    store.record_cache_hit()
    store.record_cache_miss()
    d = store.to_dict()
    assert d["cache_hits"] == 2
    assert d["cache_misses"] == 1


def test_avg_latency_multiple(store):
    store.record_compilation("svg", latency_ms=100.0)
    store.record_compilation("svg", latency_ms=200.0)
    assert store.avg_latency_ms() == 150.0


def test_uptime_positive(store):
    time.sleep(0.05)
    assert store.uptime_seconds() > 0


def test_reset(store):
    store.record_request()
    store.record_compilation("svg", latency_ms=50.0)
    store.record_cache_hit()
    store.reset()
    d = store.to_dict()
    assert d["total_requests"] == 0
    assert d["total_compilations"] == 0
    assert d["cache_hits"] == 0
    assert d["avg_latency_ms"] == 0.0
