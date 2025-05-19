# FILE: flexiai/channels/redis_channel.py

"""
Redis channel implementation.

Publishes events to a Redis Pub/Sub channel.
"""

import logging
import json
from typing import Any
import redis
from flexiai.channels.base_channel import BaseChannel

logger = logging.getLogger(__name__)


class RedisChannel(BaseChannel):
    """Channel that publishes events to Redis Pub/Sub."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", channel: str = "events"):
        """Initialize the Redis client and channel name.

        Args:
            redis_url (str): Redis connection URL.
            channel (str): Pub/Sub channel name.
        """
        self.client = redis.Redis.from_url(redis_url)
        self.channel = channel

    def publish_event(self, event: Any) -> None:
        """Publish an event by serializing it to JSON and sending to Redis.

        Args:
            event (Any): The event object or data to publish.

        Returns:
            None

        Logs:
            ERROR: Any exceptions encountered during serialization or publish.
        """
        try:
            event_json = json.dumps(event, default=str)
            self.client.publish(self.channel, event_json)
        except Exception as e:
            logger.error("Error publishing event to Redis: %s", e, exc_info=True)
