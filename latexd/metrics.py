"""Request and compilation metrics tracking for latexd."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MetricsStore:
    total_requests: int = 0
    total_compilations: int = 0
    compilation_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    format_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    latencies_ms: List[float] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    def record_request(self):
        self.total_requests += 1

    def record_compilation(self, fmt: str, error: bool = False, latency_ms: float = 0.0):
        self.total_compilations += 1
        self.format_counts[fmt] += 1
        if error:
            self.compilation_errors += 1
        if latency_ms > 0:
            self.latencies_ms.append(latency_ms)

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_cache_miss(self):
        self.cache_misses += 1

    def avg_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return sum(self.latencies_ms) / len(self.latencies_ms)

    def uptime_seconds(self) -> float:
        return time.time() - self.started_at

    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "total_compilations": self.total_compilations,
            "compilation_errors": self.compilation_errors,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "format_counts": dict(self.format_counts),
            "avg_latency_ms": round(self.avg_latency_ms(), 3),
            "uptime_seconds": round(self.uptime_seconds(), 2),
        }

    def reset(self):
        self.total_requests = 0
        self.total_compilations = 0
        self.compilation_errors = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.format_counts = defaultdict(int)
        self.latencies_ms = []
        self.started_at = time.time()


_store = MetricsStore()


def get_metrics() -> MetricsStore:
    return _store
