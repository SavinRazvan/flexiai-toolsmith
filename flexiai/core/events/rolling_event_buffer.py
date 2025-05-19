# FILE: flexiai/core/events/rolling_event_buffer.py

"""
Buffer for storing partial and finalized events for SSE replay.

Supports adding text chunks, finalizing messages, and replaying
past events after a given message ID.
"""

import logging
from collections import OrderedDict
from typing import Dict, List



class RollingEventBuffer:
    """Maintains partial chunks and finalized messages with capped capacity."""

    def __init__(self, max_size: int = 50) -> None:
        """Initialize the buffer with given capacity.

        Args:
            max_size (int): Maximum number of finalized messages to retain.
        """
        self.max_size = max_size
        self.partial_chunks: Dict[str, List[str]] = {}
        self.final_messages: "OrderedDict[str, dict]" = OrderedDict()
        
        self.logger = logging.getLogger(__name__)
        

    def add_partial_chunk(self, message_id: str, chunk_text: str) -> None:
        """Store a partial text chunk for a message.

        Args:
            message_id (str): Identifier of the message being streamed.
            chunk_text (str): New text chunk to append.

        Returns:
            None
        """
        if not message_id:
            self.logger.debug("add_partial_chunk called without message_id; skipping.")
            return

        self.partial_chunks.setdefault(message_id, []).append(chunk_text)
        self.logger.debug(f"[add_partial_chunk] '{message_id}': +'{chunk_text}'")

    def finalize_message(self, message_id: str, event_data: dict) -> None:
        """Combine partial chunks into final content and store the event.

        Args:
            message_id (str): Identifier of the message to finalize.
            event_data (dict): Event payload to annotate with final content.

        Returns:
            None
        """
        if not message_id:
            self.logger.debug("finalize_message called without message_id; skipping.")
            return

        chunks = self.partial_chunks.pop(message_id, [])
        combined = "".join(chunks)
        event_data.setdefault("content", []).append(combined)
        self.final_messages[message_id] = event_data
        self._enforce_capacity()
        self.logger.debug(f"[finalize_message] '{message_id}' finalized with '{combined}'")

    def _enforce_capacity(self) -> None:
        """Evict oldest finalized messages if capacity exceeded."""
        while len(self.final_messages) > self.max_size:
            old_id, _ = self.final_messages.popitem(last=False)
            self.logger.debug(f"[enforce_capacity] Evicted '{old_id}'")

    def get_replay_after(self, last_message_id: str) -> List[dict]:
        """Retrieve finalized messages following a given ID.

        Args:
            last_message_id (str): ID after which to replay messages.
                If empty or not found, replay all.

        Returns:
            List[dict]: List of event_data dicts in insertion order.
        """
        results: List[dict] = []
        found = (last_message_id == "")
        for mid, data in self.final_messages.items():
            if found:
                results.append(data)
            elif mid == last_message_id:
                found = True
        return results
