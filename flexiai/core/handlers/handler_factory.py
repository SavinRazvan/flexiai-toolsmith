# FILE: flexiai/core/handlers/handler_factory.py

"""
Handler factory module.

Provides a convenience function to construct an EventHandler
and optionally wire it to an EventDispatcher.
"""

from __future__ import annotations
from typing import Any, Dict, Callable, Optional

from flexiai.core.handlers.event_handler import EventHandler
from flexiai.core.handlers.run_thread_manager import RunThreadManager
from flexiai.core.handlers.event_dispatcher import EventDispatcher


def create_event_handler(
    client: Any,
    assistant_id: str,
    run_thread_manager: RunThreadManager,
    agent_actions: Dict[str, Callable],
    user_id: str,
    use_event_dispatcher: bool = True
) -> EventHandler:
    """Factory to create and configure an EventHandler.

    Instantiates an EventHandler with the provided dependencies,
    wires in the end-user ID, and optionally attaches an EventDispatcher.

    Args:
        client (Any): The AI or service client for backend interactions.
        assistant_id (str): Unique identifier for the assistant.
        run_thread_manager (RunThreadManager): Manages threads and runs.
        agent_actions (Dict[str, Callable]): Mapping of tool names to callables.
        user_id (str): Unique identifier for the end user/session.
        use_event_dispatcher (bool): If True, create and link an EventDispatcher.

    Returns:
        EventHandler: A fully configured event handler instance.
    """
    # 1) Instantiate the core EventHandler
    event_handler = EventHandler(
        client=client,
        assistant_id=assistant_id,
        run_thread_manager=run_thread_manager,
        agent_actions=agent_actions,
        event_dispatcher=None
    )

    # 2) Bind the user_id so every callback has it
    event_handler.current_user_id = user_id

    # 3) Optionally wire up the dispatcher
    if use_event_dispatcher:
        dispatcher = EventDispatcher(event_handler=event_handler)
        event_handler.event_dispatcher = dispatcher

    return event_handler
