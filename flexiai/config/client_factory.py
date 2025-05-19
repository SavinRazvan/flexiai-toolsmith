# FILE: flexiai/config/client_factory.py

"""
Factory for obtaining a singleton AI client via the unified CredentialManager.

Provides both a synchronous `get_client()` for CLI usage and an asynchronous
`get_client_async()` for web (Quart) contexts, returning the same cached client.
"""

import logging
import asyncio
from typing import Any
from flexiai.credentials.credentials import get_client as get_unified_client

logger = logging.getLogger(__name__)
_client: Any = None


def get_client() -> Any:
    """Retrieve or create and cache a single AI client instance (sync).

    Uses the unified credential manager to construct the client on first call,
    then returns the cached instance on subsequent calls.

    Returns:
        Any: A configured AI client instance.

    Raises:
        Exception: Propagates any errors from the underlying client creation.
    """
    global _client
    if _client is None:
        try:
            _client = get_unified_client()
            logger.info("[get_client] Client successfully created from unified CredentialManager.")
        except Exception as e:
            logger.error("[get_client] Error creating client", exc_info=True)
            raise
    return _client


async def get_client_async() -> Any:
    """Asynchronously retrieve or create the singleton AI client.

    Wraps the synchronous `get_client()` in a threadpool so it can be awaited
    without blocking the Quart event loop.

    Returns:
        Any: A configured AI client instance.

    Raises:
        Exception: Propagates any errors from the underlying client creation.
    """
    # If the client is already created, return it immediately.
    global _client
    if _client is not None:
        return _client

    # Otherwise, build it off the event loop.
    loop = asyncio.get_running_loop()
    try:
        _client = await loop.run_in_executor(None, get_client)
        logger.info("[get_client_async] Client successfully created in executor.")
    except Exception as e:
        logger.error("[get_client_async] Error creating client in executor", exc_info=True)
        raise
    return _client
