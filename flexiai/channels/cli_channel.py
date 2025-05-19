# FILE: flexiai/channels/cli_channel.py

"""
CLI channel implementation.

Publishes events by printing their content to the console.
"""

import logging
from typing import Any
from flexiai.channels.base_channel import BaseChannel

logger = logging.getLogger(__name__)


class CLIChannel(BaseChannel):
    """Channel that outputs events to the command line interface."""

    def publish_event(self, event: Any) -> None:
        """Publish an event to the CLI by printing its content.

        Converts the event to a dictionary (if it's a Pydantic model or dict),
        then prints each text chunk in the `content` list. Falls back to printing
        the `event` field if no `content` is provided.

        Args:
            event (Any): The event to publish. Expected to be a Pydantic model
                or a dict with a `content` key containing a list of strings.

        Returns:
            None

        Logs:
            INFO: Entry and total chunk count or fallback.
            DEBUG: Conversion and per‐chunk details.
            ERROR: Any exceptions encountered during printing.
        """
        # logger.info("CLIChannel.publish_event called")
        try:
            # Convert to dict if necessary
            if hasattr(event, "model_dump"):
                event_dict = event.model_dump()
                logger.debug("Converted Pydantic model to dict: %s", event_dict)
            elif isinstance(event, dict):
                event_dict = event
                logger.debug("Received dict event: %s", event_dict)
            else:
                event_dict = {"event": str(event)}
                logger.debug("Wrapped non-dict event into dict: %s", event_dict)

            # Extract content
            content = event_dict.get("content")
            if content:
                # logger.info("Publishing %d content chunks", len(content))
                for idx, chunk in enumerate(content):
                    # logger.debug("Printing chunk %d: %r", idx, chunk)
                    print(chunk, end="", flush=True)
            else:
                fallback = event_dict.get("event", "")
                logger.info("No content key found, printing fallback event")
                # logger.debug("Fallback event value: %r", fallback)
                print(fallback, end="", flush=True)

        except Exception as e:
            logger.error("Error publishing event to CLI: %s", e, exc_info=True)
