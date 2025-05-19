# FILE: flexiai/channels/quart_channel.py

import logging
import json
from typing import Any
from pydantic import BaseModel
from quart import g, has_request_context

from flexiai.channels.base_channel import BaseChannel
from flexiai.core.events.sse_manager import global_sse_manager

logger = logging.getLogger(__name__)

class QuartChannel(BaseChannel):
    """
    Publishes chat events to web clients via Server-Sent Events (SSE).
    """

    def publish_event(self, event: Any) -> None:
        logger.debug("QuartChannel.publish_event called with event: %r", event)
        try:
            # 1) Normalize event to a dict
            if isinstance(event, dict):
                evt = event.copy()
            elif isinstance(event, BaseModel):
                evt = event.model_dump()
            else:
                # Fallback: wrap any .data attribute
                raw = getattr(event, "data", {})
                if isinstance(raw, BaseModel):
                    raw = raw.model_dump()
                evt = {"data": raw}
                # preserve event_type if present on the object
                if hasattr(event, "event_type"):
                    evt["event_type"] = getattr(event, "event_type")

            # 2) Ensure evt["data"] is a plain dict
            data = evt.get("data", {})
            if not isinstance(data, dict):
                try:
                    data = dict(data)
                except Exception:
                    data = {}

            # 3) Inject user_id from cookie/context if missing
            user_id = data.get("user_id")
            if not user_id and has_request_context():
                user_id = getattr(g, "user_id", None)
                if user_id:
                    data["user_id"] = user_id

            if not user_id:
                logger.error(
                    "QuartChannel.publish_event: missing user_id in event.data, dropping event: %s",
                    evt
                )
                return

            # 4) Put the possibly-updated data back
            evt["data"] = data

            # 5) (Optional) Log the outgoing JSON
            try:
                evt_json = json.dumps(evt, default=str)
                # logger.debug("Serialized event JSON: %s", evt_json)
            except Exception:
                pass

            # 6) Enqueue for SSE
            global_sse_manager.put_event(user_id, evt)
            # logger.debug("Enqueued event to SSEManager for user_id='%s'", user_id)

        except Exception as e:
            logger.error("QuartChannel.publish_event error: %s", e, exc_info=True)
