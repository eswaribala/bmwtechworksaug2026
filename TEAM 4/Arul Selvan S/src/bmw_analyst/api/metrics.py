from collections import Counter
from threading import Lock


_counters: Counter[str] = Counter()
_lock = Lock()


def increment(name: str) -> None:
    with _lock:
        _counters[name] += 1


def snapshot() -> dict[str, int]:
    with _lock:
        return dict(_counters)