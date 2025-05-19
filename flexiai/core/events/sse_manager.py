# FILE: flexiai/core/events/sse_manager.py

from collections import defaultdict, deque
import threading
import logging

logger = logging.getLogger(__name__)

class SSEManager:
    _locks: dict[str, threading.Lock] = defaultdict(threading.Lock)
    _queues: dict[str, deque[dict]] = defaultdict(deque)

    @classmethod
    def put_event(cls, user_id: str, event: dict) -> None:
        lock = cls._locks[user_id]
        with lock:
            cls._queues[user_id].append(event)
            # logger.debug(f"[SSEManager.put_event] queued for {user_id}: {event.get('event_type')}")

    @classmethod
    def get_events(cls, user_id: str) -> list[dict]:
        lock = cls._locks[user_id]
        with lock:
            q = cls._queues[user_id]
            items = list(q)
            q.clear()
            # logger.debug(f"[SSEManager.get_events] drained {len(items)} events for {user_id}")
            return items

# ─── Module‐level singleton for easy import ────────────────────────────
global_sse_manager = SSEManager()