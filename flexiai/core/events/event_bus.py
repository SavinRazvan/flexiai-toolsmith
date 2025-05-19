# FILE: flexiai/core/events/event_bus.py

"""
In-memory publish/subscribe event bus.

Allows subscription to event types, unsubscription, and publishing events
to all registered callbacks.
"""

import logging
from typing import Any, Callable, Dict, List


class EventBus:
    """A simple in-memory event bus for publishing and subscribing to events."""

    def __init__(self) -> None:
        """Initialize the EventBus with no subscribers."""
        self.logger = logging.getLogger(__name__)
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}
        self.logger.info("[EventBus] Initialized.")

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Register a callback for a specific event type.

        Args:
            event_type (str): The event type to subscribe to.
            callback (Callable[[Any], None]): Function to call when the event fires.

        Returns:
            None

        Logs:
            DEBUG: When a new subscriber list is created.
            INFO: When a callback is successfully subscribed.
            WARNING: If the callback is already subscribed.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            # self.logger.debug(f"[subscribe] Created subscriber list for '{event_type}'.")

        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            # self.logger.info(f"[subscribe] Subscribed '{callback.__name__}' to '{event_type}'.")
        else:
            self.logger.warning(f"[subscribe] '{callback.__name__}' already subscribed to '{event_type}'.")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Unregister a callback from a specific event type.

        Args:
            event_type (str): The event type to unsubscribe from.
            callback (Callable[[Any], None]): The callback to remove.

        Returns:
            None

        Logs:
            INFO: When a callback is successfully unsubscribed.
            WARNING: If the callback was not found.
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.info(f"[unsubscribe] Unsubscribed '{callback.__name__}' from '{event_type}'.")
        else:
            self.logger.warning(f"[unsubscribe] '{callback.__name__}' not found for '{event_type}'.")

    def publish(self, event_type: str, event_data: Any) -> None:
        """Publish an event to all subscribers of the given type.

        Args:
            event_type (str): The type of event being published.
            event_data (Any): Payload of the event.

        Returns:
            None

        Logs:
            DEBUG: The event being published and empty subscriber lists.
            DEBUG: Each successful callback execution.
            ERROR: Any exceptions during callback execution.
        """
        self.logger.debug(f"[publish] Publishing '{event_type}' with data: {event_data}")
        callbacks = self.subscribers.get(event_type, [])
        if not callbacks:
            self.logger.debug(f"[publish] No subscribers for '{event_type}'.")
        for callback in callbacks:
            try:
                callback(event_data)
                self.logger.debug(f"[publish] Executed '{callback.__name__}' for '{event_type}'.")
            except Exception as e:
                self.logger.error(
                    f"[publish] Error in '{callback.__name__}' for '{event_type}': {e}",
                    exc_info=True
                )

# Global event bus instance
global_event_bus = EventBus()
