# FILE: flexiai/channels/base_channel.py

"""
Abstract base classes for event channels.

Defines the BaseChannel interface that all channels must implement.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseChannel(ABC):
    """Interface for a publish/subscribe channel.

    Subclasses must implement `publish_event` to deliver events
    through a specific medium (e.g., CLI, Redis, SSE).
    """

    @abstractmethod
    def publish_event(self, event: Any) -> None:
        """Publish an event to this channel.

        Args:
            event (Any): The event object or data to be published.

        Returns:
            None
        """
        pass
