# FILE: flexiai/core/events/event_models.py

"""
Event models for internal messaging and SSE streaming.

Defines base event schema and specialized events for message deltas
and run completion notifications.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List
import time

class BaseEvent(BaseModel):
    """Base schema for all events.

    Attributes:
        event_type (str): Identifier for the type of event.
        timestamp (float): UNIX timestamp when the event was created.
        data (Dict[str, Any]): Arbitrary payload data.
    """
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    data: Dict[str, Any] = Field(default_factory=dict)

class MessageDeltaEvent(BaseEvent):
    """Event representing a streaming delta (partial) message update.

    Attributes:
        message_id (str): Unique identifier of the message.
        content (List[str]): List of text chunks to append.
    """
    message_id: str = ""
    content: List[str] = Field(default_factory=list)

class RunCompletedEvent(BaseEvent):
    """Event indicating that a run has fully completed.

    Attributes:
        run_id (str): Unique identifier of the completed run.
        status (str): Status of the run (e.g., 'completed', 'failed').
    """
    run_id: str = ""
    status: str = ""
