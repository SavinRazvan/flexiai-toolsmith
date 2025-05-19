# flexiai/core/events/session.

import threading
import asyncio
from flexiai.core.events.rolling_event_buffer import RollingEventBuffer

class ChatSession:
    def __init__(self, max_buffer: int = 50):
        # for “/ready” buffering
        self.event_buffer: list[dict] = []
        self.buffer_lock = threading.Lock()

        # flip to True once client has hit /ready
        self.ready_event = asyncio.Event()

        # stores _all_ partial + finalized chunks so we can replay after a reconnect
        self.rolling_buffer = RollingEventBuffer(max_size=max_buffer)

        # the thread_id for this user’s conversation
        self.thread_id: str | None = None
