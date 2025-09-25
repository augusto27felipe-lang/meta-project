import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Event:
    type: str
    payload: Any
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventBus:
    """Thread-safe publish-subscribe event bus.

    Each subscriber gets its own internal queue so multiple consumers receive the same events.
    """

    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def publish(self, event: Event):
        with self._lock:
            for q in list(self._subscribers):
                try:
                    q.put(event)
                except Exception:
                    pass

    def register(self, maxsize: int = 0) -> queue.Queue:
        """Register a new subscriber and return a Queue the subscriber can read from."""
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unregister(self, q: queue.Queue):
        with self._lock:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    def drain(self):
        # drain all subscriber queues (mainly for testing)
        out = {}
        with self._lock:
            for idx, q in enumerate(self._subscribers):
                items = []
                while True:
                    try:
                        items.append(q.get_nowait())
                    except queue.Empty:
                        break
                out[idx] = items
        return out


# Singleton default bus
_default_bus = None
_lock = threading.Lock()


def get_event_bus() -> EventBus:
    global _default_bus
    with _lock:
        if _default_bus is None:
            _default_bus = EventBus()
        return _default_bus


def run_consumer_loop(consumer: Callable[[Event], None], stop_event: threading.Event):
    bus = get_event_bus()
    q = bus.register()
    try:
        while not stop_event.is_set():
            try:
                ev = q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                consumer(ev)
            except Exception:
                # swallow to keep loop alive
                pass
    finally:
        bus.unregister(q)
