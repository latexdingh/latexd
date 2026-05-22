"""Simple in-memory rate limiting for the latexd API."""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional


class RateLimiter:
    """Sliding-window rate limiter keyed by client identifier."""

    def __init__(self, max_requests: int = 30, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        """Return True if the request is within the allowed rate."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._buckets[client_id]
            # Evict timestamps outside the window
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                return False

            bucket.append(now)
            return True

    def remaining(self, client_id: str) -> int:
        """Return how many requests the client can still make in the window."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._buckets[client_id]
            active = sum(1 for ts in bucket if ts > cutoff)
            return max(0, self.max_requests - active)

    def reset(self, client_id: Optional[str] = None) -> None:
        """Clear rate-limit state for one client or all clients."""
        with self._lock:
            if client_id is None:
                self._buckets.clear()
            else:
                self._buckets.pop(client_id, None)


# Module-level default instance (can be replaced in tests)
_limiter: RateLimiter = RateLimiter()


def get_limiter() -> RateLimiter:
    return _limiter


def set_limiter(limiter: RateLimiter) -> None:
    global _limiter
    _limiter = limiter
