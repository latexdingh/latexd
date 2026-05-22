"""Webhook notification support for async job completion."""

import hashlib
import hmac
import json
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import requests

_webhooks: Dict[str, dict] = {}
_lock = threading.Lock()


@dataclass
class WebhookEntry:
    url: str
    secret: Optional[str] = None
    events: List[str] = field(default_factory=lambda: ["job.complete", "job.error"])
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "events": self.events,
            "created_at": self.created_at,
        }


def register(url: str, secret: Optional[str] = None, events: Optional[List[str]] = None) -> str:
    """Register a webhook URL and return its ID."""
    wid = hashlib.sha256(f"{url}{time.time()}".encode()).hexdigest()[:16]
    entry = WebhookEntry(
        url=url,
        secret=secret,
        events=events or ["job.complete", "job.error"],
    )
    with _lock:
        _webhooks[wid] = entry
    return wid


def unregister(wid: str) -> bool:
    """Remove a webhook by ID. Returns True if it existed."""
    with _lock:
        return _webhooks.pop(wid, None) is not None


def list_webhooks() -> Dict[str, dict]:
    with _lock:
        return {wid: entry.to_dict() for wid, entry in _webhooks.items()}


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def _deliver(entry: WebhookEntry, event: str, data: dict) -> None:
    payload = json.dumps({"event": event, "data": data}).encode()
    headers = {"Content-Type": "application/json", "X-Latexd-Event": event}
    if entry.secret:
        headers["X-Latexd-Signature"] = _sign(payload, entry.secret)
    try:
        requests.post(entry.url, data=payload, headers=headers, timeout=5)
    except Exception:
        pass


def notify(event: str, data: dict) -> None:
    """Fire webhooks matching the given event in background threads."""
    with _lock:
        targets = [(wid, entry) for wid, entry in _webhooks.items() if event in entry.events]
    for _, entry in targets:
        t = threading.Thread(target=_deliver, args=(entry, event, data), daemon=True)
        t.start()
