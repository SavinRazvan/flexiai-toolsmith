# FILE: flexiai/controllers/cli_chat_controller.py

from __future__ import annotations
import logging
import asyncio
from logging import LoggerAdapter
from typing import Any

from flexiai.config.client_factory import get_client_async
from flexiai.core.handlers.run_thread_manager import RunThreadManager
from flexiai.toolsmith.tools_manager import ToolsManager
from flexiai.core.handlers.handler_factory import create_event_handler
from flexiai.core.events.event_bus import global_event_bus

_base_logger = logging.getLogger(__name__)


class CLIChatController:
    """Orchestrates a CLI-based chat loop with an AI assistant."""

    def __init__(
        self,
        assistant_id: str,
        client: Any,
        user_id: str
    ):
        """
        Initialize the CLIChatController with a pre-built AI client and a user_id.

        Args:
            assistant_id: Unique identifier of the assistant.
            client: Async AI client instance.
            user_id: Unique identifier for this user/session.
        """
        self.assistant_id = assistant_id
        self.user_id = user_id
        self.logger = LoggerAdapter(
            _base_logger,
            {"assistant_id": assistant_id, "user_id": user_id}
        )
        self.logger.info("Initializing CLIChatController (assistant=%s, user=%s)", assistant_id, user_id)

        # Core client and thread manager
        self.client = client
        self.run_thread_manager = RunThreadManager(self.client)
        self.logger.debug("RunThreadManager initialized")

        # Tools registry
        self.tools_manager = ToolsManager(self.client, self.run_thread_manager)
        agent_actions = self.tools_manager.tools_registry.get_all_tools()
        self.logger.debug("ToolsManager loaded %d tools", len(agent_actions))

        # Event handler + dispatcher wiring
        self.event_handler = create_event_handler(
            client=self.client,
            assistant_id=self.assistant_id,
            run_thread_manager=self.run_thread_manager,
            agent_actions=agent_actions,
            user_id=self.user_id,
            use_event_dispatcher=True
        )
        self.event_handler.event_queue = asyncio.Queue()
        self.logger.debug("EventHandler and event_queue initialized")

        # Subscribe to all dispatchable events
        events = list(self.event_handler.event_dispatcher.event_map)
        self.logger.debug("Subscribing to %d events", len(events))
        for ev in events:
            global_event_bus.subscribe(ev, self.complete_event_callback)
            self.logger.debug("Subscribed to event '%s'", ev)
        self.logger.info("Subscribed to all CLI events")

        # Will be set in create_async
        self.thread_id: str | None = None

    @classmethod
    async def create_async(
        cls,
        assistant_id: str,
        user_id: str
    ) -> CLIChatController:
        """
        Async factory to build the controller: initializes client, thread, and logger.

        Args:
            assistant_id: Assistant identifier.
            user_id: Unique identifier for this user/session.

        Returns:
            CLIChatController: Fully initialized controller.
        """
        _base_logger.info("CLIChatController.create_async: creating client")
        client = await get_client_async()
        _base_logger.info("Async client created")

        self = cls(assistant_id, client, user_id)

        thread_id = await self.run_thread_manager.get_or_create_thread(
            assistant_id, user_id=user_id
        )
        self.thread_id = thread_id
        self.logger = LoggerAdapter(
            _base_logger,
            {"assistant_id": assistant_id, "thread_id": thread_id, "user_id": user_id}
        )
        self.logger.info("CLIChatController initialized with thread_id: %s", thread_id)
        return self

    def complete_event_callback(self, event: dict) -> None:
        """Enqueue completed or delta events for processing."""
        try:
            et = event.get("event_type")
            self.logger.debug("Event received: %s", et)
            self.event_handler.event_queue.put_nowait(event)
            self.logger.debug("Event enqueued: %s", et)
        except Exception as e:
            self.logger.error("Failed to enqueue event: %s", e, exc_info=True)

    async def process_user_message(self, message: str) -> None:
        """Add a user message to the thread and start the assistant run asynchronously."""
        self.logger.info("Processing user message: %r", message)
        # Reset event queue
        self.event_handler.event_queue = asyncio.Queue()
        self.logger.debug("Event queue reset")

        try:
            await self.run_thread_manager.add_message_to_thread(
                self.thread_id, message, user_id=self.user_id
            )
            self.logger.debug("Message added to thread '%s'", self.thread_id)
        except Exception as e:
            self.logger.error("Error adding message to thread: %s", e, exc_info=True)
            return

        try:
            asyncio.create_task(
                self.event_handler.start_run(
                    self.assistant_id,
                    self.thread_id,
                    self.user_id
                )
            )
            self.logger.info("Assistant run started")
        except Exception as e:
            self.logger.error("Failed to start assistant run: %s", e, exc_info=True)

    async def await_run_completion(self) -> bool:
        """Wait for streaming delta chunks and final completion events."""
        self.logger.debug("Waiting for events on queue")
        while True:
            try:
                event = await self.event_handler.event_queue.get()
                et = event.get("event_type")

                if et in {"thread.message.delta", "message_delta"}:
                    content = event.get("content", [])
                    self.logger.debug("Received %d chunks for event %s", len(content), et)
                    for idx, chunk in enumerate(content):
                        print(chunk, end="", flush=True)
                        self.logger.debug("Printed chunk %d: %r", idx, chunk)
                    continue

                if et in {"message_completed", "thread.run.completed", "done"}:
                    self.logger.info("Received completion event: %s", et)
                    break

                self.logger.warning("Unexpected event type: %s", et)
            except Exception as e:
                self.logger.error("Error processing event: %s", e, exc_info=True)
                return False

        return True

    async def run_chat_loop(
        self,
        user_name: str = "User",
        assistant_name: str = "Assistant"
    ) -> None:
        """Run the interactive chat loop until the user exits."""
        print("======================================")
        print("         FlexiAI Chat Session         ")
        print("======================================")
        print("Type 'exit' or '/exit' to quit the conversation.\n")

        while True:
            try:
                user_message = await asyncio.to_thread(
                    input, f"{user_name}: "
                )
            except Exception as e:
                self.logger.error("Error reading input: %s", e, exc_info=True)
                return

            if user_message.strip().lower() in {"exit", "/exit"}:
                self.logger.info("Exiting chat as per user request.")
                print("Exiting chat...")
                return

            await self.process_user_message(user_message)
            print(f"{assistant_name}:", end=" ", flush=True)
            await self.await_run_completion()
            print()
