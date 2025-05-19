# FILE: flexiai/channels/multi_channel_publisher.py

"""
Multi-channel publisher.

Fan-out publishing to all channels specified in ACTIVE_CHANNELS.
"""

import logging
from typing import Any
from flexiai.channels.channel_manager import get_active_channels

logger = logging.getLogger(__name__)


class MultiChannelPublisher:
    """Publishes events to multiple channels simultaneously."""

    def __init__(self) -> None:
        """Initialize the publisher with the currently active channels."""
        self.channels = get_active_channels()

    def publish(self, event_type: str, event_data: Any) -> None:
        """Publish an event to all active channels.

        Args:
            event_type (str): The type of the event being published.
            event_data (Any): The payload or event object to publish.

        Returns:
            None

        Logs:
            ERROR: Any exceptions from individual channel publishing are caught and
                logged, allowing other channels to proceed.
        """
        for channel in self.channels:
            try:
                channel.publish_event(event_data)
            except Exception as e:
                logger.error(
                    "Error publishing to channel %s: %s",
                    type(channel).__name__,
                    e,
                    exc_info=True
                )
