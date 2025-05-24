# FILE: flexiai/controllers/quart_chat_controller.py

import asyncio
import json
import threading
import logging
from typing import Optional
from quart import Blueprint, request, jsonify, render_template, Response, g

from flexiai.config.models import GeneralSettings
from flexiai.config.client_factory import get_client_async
from flexiai.core.handlers.run_thread_manager import RunThreadManager
from flexiai.toolsmith.tools_manager import ToolsManager
from flexiai.core.events.event_bus import global_event_bus
from flexiai.core.events.sse_manager import SSEManager

chat_bp = Blueprint('chat', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

# ─── Controller Singleton ──────────────────────────────────────────────
controller_instance: Optional["QuartChatController"] = None

# load & validate .env right away
settings = GeneralSettings()


class QuartChatController:
    """Manages chat sessions over HTTP with SSE for continuous assistant streaming."""

    def __init__(self, assistant_id: str, client) -> None:
        self.assistant_id = assistant_id
        self.logger = logger.getChild("QuartChatController")
        self.loop = asyncio.get_event_loop()

        # — Core AI client + thread manager
        self.client = client
        self.run_thread_manager = RunThreadManager(self.client)

        # — Tools registry
        self.tools_manager = ToolsManager(
            client=self.client,
            run_thread_manager=self.run_thread_manager
        )
        agent_actions = self.tools_manager.tools_registry.get_all_tools()

        # ── lazy import to break the circular dependency ──────────────────────
        from flexiai.core.handlers.handler_factory import create_event_handler

        # — Event handler + dispatcher wiring; placeholder user_id overwritten per request
        self.event_handler = create_event_handler(
            client=self.client,
            assistant_id=self.assistant_id,
            run_thread_manager=self.run_thread_manager,
            agent_actions=agent_actions,
            user_id="",  # will be set in process_user_message()
            use_event_dispatcher=True
        )
        self.event_handler.event_queue = asyncio.Queue()

        # — Subscribe to *all* dispatchable events
        for ev in self.event_handler.event_dispatcher.event_map:
            global_event_bus.subscribe(ev, self._on_event)
            self.logger.debug(f"[__init__] Subscribed to event '{ev}'")

        # — Internal buffer + sync for initial flush
        self.event_buffer: list[dict] = []
        self.event_buffer_lock = threading.Lock()
        self.client_ready_event = asyncio.Event()
        self.thread_id: Optional[str] = None

        self.logger.info("[__init__] Initialized controller for assistant '%s'.", assistant_id)

    @classmethod
    async def create_async(cls) -> "QuartChatController":
        """
        Factory: asynchronously create the controller singleton (no thread yet).
        """
        global controller_instance

        assistant_id = settings.ASSISTANT_ID
        if not assistant_id:
            logger.error("ASSISTANT_ID is missing—please set it in your .env")
            raise RuntimeError("Missing ASSISTANT_ID")

        client = await get_client_async()
        self = cls(assistant_id, client)
        controller_instance = self

        # thread creation is deferred until we know g.user_id
        return self

    def _on_event(self, event: dict) -> None:
        """
        Global event-bus callback.
        1) inject user_id
        2) buffer until /ready
        3) always feed the EventHandler queue
        4) once live, forward to SSEManager
        """
        uid = self.event_handler.current_user_id or event.get("data", {}).get("user_id")
        event.setdefault("data", {})["user_id"] = uid

        with self.event_buffer_lock:
            self.event_buffer.append(event)

        self.loop.call_soon_threadsafe(
            self.event_handler.event_queue.put_nowait, event
        )

        if self.client_ready_event.is_set() and uid:
            SSEManager.put_event(uid, event)

    async def process_user_message(self, message: str) -> None:
        """
        Handle an incoming user message: set user_id, clear buffers, create thread if needed, and start a new run.
        """
        user_id = g.user_id
        self.logger.info("[process_user_message] %r (user_id=%s)", message, user_id)

        # Lazy-create the assistant thread for this user session
        if self.thread_id is None:
            self.thread_id = await self.run_thread_manager.get_or_create_thread(
                self.assistant_id,
                user_id=user_id,
            )
            self.logger.info(
                "[process_user_message] Created thread '%s' for user_id '%s'",
                self.thread_id, user_id
            )

        # Bind user_id into handler so all callbacks carry it
        self.event_handler.current_user_id = user_id

        # Reset event queue + buffer
        self.event_handler.event_queue = asyncio.Queue()
        with self.event_buffer_lock:
            self.event_buffer.clear()
        self.client_ready_event.clear()

        # Post the user message (metadata=user_id)
        await self.run_thread_manager.add_message_to_thread(
            self.thread_id, message, user_id=user_id
        )

        # Kick off streaming run, passing user_id
        asyncio.create_task(
            self.event_handler.start_run(
                self.assistant_id, self.thread_id, user_id
            )
        )

    async def await_run_completion(self) -> bool:
        """
        Wait until the assistant run emits a completion event.
        """
        while True:
            ev = await self.event_handler.event_queue.get()
            if ev.get("event_type") in ("message_completed", "thread.run.completed", "done"):
                return True

    @chat_bp.route('/ready', methods=['POST'])
    async def ready():
        """
        Client calls this to flush buffered events and go live.
        """
        user_id = g.user_id
        await controller_instance.flush_event_buffer(user_id)
        return jsonify({"status": "ready"}), 200

    async def flush_event_buffer(self, user_id: str) -> None:
        """
        Drain our internal buffer into the SSEManager, then mark the client as live.
        """
        with self.event_buffer_lock:
            buffered = list(self.event_buffer)
            self.event_buffer.clear()

        for ev in buffered:
            SSEManager.put_event(user_id, ev)

        self.client_ready_event.set()

    @chat_bp.route('/assistant_stream_message', methods=['GET'])
    async def assistant_stream_message():
        """
        SSE endpoint: streams queued events for this user.
        """
        user_id = g.user_id
        logger.info(f"[assistant_stream_message] SSE client connected for user_id '{user_id}'")

        async def event_generator():
            try:
                yield "retry:1000\n\n"
                await controller_instance.client_ready_event.wait()

                while True:
                    for ev in SSEManager.get_events(user_id):
                        msg_id = ev.get("message_id") or ev.get("data", {}).get("id")
                        if msg_id:
                            yield f"id: {msg_id}\n"
                        et = ev.get("event_type", "message_delta")
                        yield f"event: {et}\n"
                        yield f"data: {json.dumps(ev, default=str)}\n\n"

                    yield ": keep-alive\n\n"
                    await asyncio.sleep(0.3)

            except asyncio.CancelledError:
                logger.info(f"[assistant_stream_message] Disconnected '{user_id}'")
            except Exception as ex:
                logger.exception(
                    f"[assistant_stream_message] Unexpected error for '{user_id}': {ex}"
                )

        headers = {
            "Content-Type":      "text/event-stream; charset=utf-8",
            "Cache-Control":     "no-cache, no-transform",
            "Connection":        "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return Response(event_generator(), headers=headers)

    @chat_bp.route('/', methods=['GET'])
    async def render_chat_page():
        """
        Render the full-page chat UI.
        """
        logger.info(
            "[route /] Rendering chat page for assistant '%s'",
            controller_instance.assistant_id
        )
        return await render_template('chat.html')

    @chat_bp.route('/user_send_message', methods=['POST'])
    async def user_send_message():
        """
        Receive user input, trigger processing, and await completion.
        """
        data = await request.get_json()
        msg = data.get("message")
        if not msg:
            return jsonify({"error": "No message provided"}), 400

        await controller_instance.process_user_message(msg)
        await controller_instance.await_run_completion()
        return jsonify({"status": "success"}), 200


# ─── Initialize singleton to None ────────────────────────────────────────
controller_instance = None
