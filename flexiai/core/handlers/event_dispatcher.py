# FILE: flexiai/core/handlers/event_dispatcher.py

"""
Event dispatcher module.

Routes incoming events to the appropriate EventHandler methods
based on their `event_type`.
"""

from __future__ import annotations
from typing import Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)

class EventDispatcher:
    """Dispatches events from the core to EventHandler callbacks."""

    def __init__(self, event_handler: Any) -> None:
        """Initialize the EventDispatcher with a reference to the EventHandler.

        Builds a mapping from event_type strings to handler methods.

        Args:
            event_handler (Any): The EventHandler instance whose methods will be invoked.
        """
        self.event_handler = event_handler

        # Map event types to their corresponding EventHandler methods.
        # Includes legacy SSE, thread, run, and message events.
        self.event_map: Dict[str, Callable[[Any, str], None]] = {
            # Thread lifecycle
            'thread.created': self.event_handler._handle_thread_created,

            # Run lifecycle
            'thread.run.created': self.event_handler._handle_run_created,
            'thread.run.queued': self.event_handler._handle_run_queued,
            'thread.run.in_progress': self.event_handler._handle_run_in_progress,
            'thread.run.requires_action': self.event_handler._handle_run_requires_action,
            'thread.run.completed': self.event_handler._handle_run_completed,
            'thread.run.incomplete': self.event_handler._handle_run_incomplete,
            'thread.run.failed': self.event_handler._handle_run_failed,
            'thread.run.cancelling': self.event_handler._handle_run_cancelling,
            'thread.run.cancelled': self.event_handler._handle_run_cancelled,
            'thread.run.expired': self.event_handler._handle_run_expired,

            # Run step events
            'thread.run.step.created': self.event_handler._handle_run_step_created,
            'thread.run.step.in_progress': self.event_handler._handle_run_step_in_progress,
            'thread.run.step.delta': self.event_handler._handle_run_step_delta,
            'thread.run.step.completed': self.event_handler._handle_run_step_completed,
            'thread.run.step.failed': self.event_handler._handle_run_step_failed,
            'thread.run.step.cancelled': self.event_handler._handle_run_step_cancelled,
            'thread.run.step.expired': self.event_handler._handle_run_step_expired,

            # Message events
            'thread.message.created': self.event_handler._handle_message_created,
            'thread.message.in_progress': self.event_handler._handle_message_in_progress,
            'thread.message.delta': self.event_handler._handle_message_delta,
            'thread.message.completed': self.event_handler._handle_message_completed,
            'thread.message.incomplete': self.event_handler._handle_message_incomplete,

            # SSE delta events
            'tool_call_delta': self.event_handler._handle_delta,
            'message_delta': self.event_handler._handle_delta,

            # Error and done
            'error': self.event_handler._handle_error_event,
            'done': self.event_handler._handle_done_event,
        }

    def dispatch(self, event_type: str, event_data: Any, thread_id: str) -> None:
        """Dispatch an event to its corresponding handler.

        Looks up `event_type` in the internal map and invokes the
        associated method on the EventHandler. Unhandled types
        are delegated.

        Args:
            event_type (str): The type identifier of the event.
            event_data (Any): The raw event payload.
            thread_id (str): The thread ID associated with the event.

        Returns:
            None
        """
        handler = self.event_map.get(event_type)
        if handler:
            # logger.debug(
            #     f"[dispatch] Dispatching '{event_type}' for thread '{thread_id}' and raw event payload is {event_data}."
            # )
            handler(event_data, thread_id)
            if event_type in ["done", "thread.run.completed", "message_completed"]:
                logger.debug(
                    f"[dispatch] '{event_type}' indicates run end; ready for next input."
                )
        else:
            # No handler registered for this type
            self.event_handler._handle_unhandled_event(event_data, thread_id)
