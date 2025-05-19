# FILE: flexiai/core/handlers/run_thread_manager.py

"""
RunThreadManager module.

Manages assistant threads, messages, and runs for streaming interactions
using the async OpenAI client and asyncio Locks.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, Optional


class RunThreadManager:
    """Manages threads, runs, and messages for a FlexiAI assistant, scoped per user."""

    def __init__(self, client: Any) -> None:
        """
        Initialize the RunThreadManager.

        Args:
            client (Any): The async AI service client.
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        # Maps "{assistant_id}:{user_id}" -> {"thread_id": str, "status": str}
        # or just assistant_id if no user_id provided
        self.active_threads: Dict[str, Dict[str, str]] = {}
        # Maps thread_id -> set of processed message IDs
        self.thread_message_tracking: Dict[str, set[str]] = {}

    async def get_or_create_thread(
        self,
        assistant_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Retrieve an existing thread ID for the assistant+user, or create a new one.

        Args:
            assistant_id (str): Unique identifier of the assistant.
            user_id (Optional[str]): Unique identifier of the end user.

        Returns:
            str: The thread ID.

        Raises:
            RuntimeError: If thread creation fails.
        """
        # Build the scoping key
        key = f"{assistant_id}:{user_id}" if user_id else assistant_id
        self.logger.info(f"[get_or_create_thread] assistant_id='{assistant_id}', user_id='{user_id}'")

        async with self.lock:
            info = self.active_threads.get(key)
            if info:
                thread_id = info["thread_id"]
                self.logger.info(f"[get_or_create_thread] Found existing thread '{thread_id}' for key '{key}'")
                if await self._validate_thread(thread_id):
                    return thread_id
                self.logger.warning(f"[get_or_create_thread] Thread '{thread_id}' invalid; removing for key '{key}'")
                del self.active_threads[key]

        try:
            self.logger.info(f"[get_or_create_thread] Creating new thread for '{assistant_id}' (user '{user_id}')")
            thread = await self.client.beta.threads.create()
            thread_id = thread.id
            async with self.lock:
                self.active_threads[key] = {
                    "thread_id": thread_id,
                    "status": "initialized"
                }
            self.logger.info(f"[get_or_create_thread] Created thread '{thread_id}' for key '{key}'")
            return thread_id
        except Exception as e:
            self.logger.error(f"[get_or_create_thread] Failed to create thread: {e}", exc_info=True)
            raise RuntimeError(
                f"Unable to create thread for assistant '{assistant_id}' (user '{user_id}')"
            ) from e

    async def _validate_thread(self, thread_id: str) -> bool:
        """
        Check if the given thread ID is still valid via the API.

        Args:
            thread_id (str): The thread ID to validate.

        Returns:
            bool: True if the thread exists, False otherwise.
        """
        try:
            await self.client.beta.threads.retrieve(thread_id=thread_id)
            self.logger.debug(f"[_validate_thread] Thread '{thread_id}' is valid")
            return True
        except Exception:
            self.logger.warning(f"[_validate_thread] Thread '{thread_id}' is invalid or missing")
            return False

    async def add_message_to_thread(
        self,
        thread_id: str,
        message: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Add a user message to the specified thread, tracking duplicates.

        Args:
            thread_id (str): The thread ID.
            message (str): The message content.
            user_id (Optional[str]): Unique identifier of the end user.

        Returns:
            str: The message ID returned by the API.

        Raises:
            ValueError: If the message is empty.
            RuntimeError: If the API call fails.
        """
        if not message.strip():
            self.logger.warning(f"[add_message_to_thread] Empty message for thread '{thread_id}'")
            raise ValueError("Message cannot be empty")

        try:
            self.logger.info(f"[add_message_to_thread] Thread '{thread_id}': adding message (user '{user_id}')")

            # Build kwargs dynamically so we only send metadata if user_id provided
            kwargs: Dict[str, Any] = {
                "thread_id": thread_id,
                "content": message,
                "role": "user"
            }
            if user_id is not None:
                # inject user_id into metadata
                kwargs["metadata"] = {"user_id": user_id}

            resp = await self.client.beta.threads.messages.create(**kwargs)
            message_id = resp.id

            async with self.lock:
                seen = self.thread_message_tracking.setdefault(thread_id, set())
                if message_id in seen:
                    self.logger.warning(f"[add_message_to_thread] Duplicate message '{message_id}'")
                else:
                    seen.add(message_id)

            self.logger.info(f"[add_message_to_thread] Added message '{message_id}'")
            return message_id
        except Exception as e:
            self.logger.error(f"[add_message_to_thread] Error: {e}", exc_info=True)
            raise RuntimeError(f"Error adding message to thread '{thread_id}'") from e

    async def start_run(self, assistant_id: str, thread_id: str) -> Any:
        """
        Start a streaming run for the assistant in the specified thread.

        Args:
            assistant_id (str): Assistant identifier.
            thread_id (str): Thread identifier.

        Returns:
            Any: An async iterator of streaming events.

        Raises:
            Exception: If the API call fails.
        """
        self.logger.info(f"[start_run] assistant='{assistant_id}', thread='{thread_id}'")
        try:
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                stream=True
            )
            self.logger.debug("[start_run] Run created")
            return run
        except Exception as e:
            self.logger.error(f"[start_run] Error starting run: {e}", exc_info=True)
            raise

    def submit_tool_outputs_stream(self, thread_id: str, run_id: str, tool_outputs: Any):
        """
        Submit tool outputs in streaming mode back to the run.

        Args:
            thread_id (str): Thread identifier.
            run_id (str): Run identifier.
            tool_outputs (Any): List of tool output dicts.

        Returns:
            AsyncAssistantStreamManager: The stream manager you can `async with`.
        """
        self.logger.info(f"[submit_tool_outputs_stream] run='{run_id}', thread='{thread_id}'")
        return self.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )

    async def submit_tool_outputs(self, thread_id: str, run_id: str, tool_outputs: Any) -> Any:
        """
        Submit tool outputs without streaming.

        Args:
            thread_id (str): Thread identifier.
            run_id (str): Run identifier.
            tool_outputs (Any): List of tool output dicts.

        Returns:
            Any: API response.

        Raises:
            Exception: If the submission fails.
        """
        self.logger.info(f"[submit_tool_outputs] run='{run_id}', thread='{thread_id}'")
        try:
            resp = await self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            self.logger.debug("[submit_tool_outputs] Submission succeeded")
            return resp
        except Exception as e:
            self.logger.error(f"[submit_tool_outputs] Error: {e}", exc_info=True)
            raise

    def track_assistant_in_thread(
        self,
        assistant_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Retrieve the active thread information for the given assistant+user.

        Args:
            assistant_id (str): Assistant identifier.
            user_id (Optional[str]): End-user identifier.

        Returns:
            Optional[Dict[str, str]]: Thread info if tracked, else None.
        """
        if user_id:
            key = f"{assistant_id}:{user_id}"
            info = self.active_threads.get(key)
            if info:
                return info
        # fallback to assistant-only thread if present
        return self.active_threads.get(assistant_id)

    async def extract_run_id(
        self,
        event_or_run_obj: Any,
        thread_id: str,
        assistant_id: Optional[str] = None,
        stream: Optional[bool] = None
    ) -> Optional[str]:
        """
        Extract the run ID from a run object or the first event in a streaming iterator.

        Args:
            event_or_run_obj (Any): Run object or async iterator.
            thread_id (str): Thread identifier.
            assistant_id (Optional[str]): Assistant identifier.
            stream (Optional[bool]): Whether streaming mode was used.

        Returns:
            Optional[str]: The extracted run ID, or None if not found.
        """
        try:
            rid = getattr(event_or_run_obj, "id", None)
            if rid:
                self.logger.debug(f"[extract_run_id] Found run ID '{rid}'")
                return rid

            if stream and hasattr(event_or_run_obj, "__aiter__"):
                ait = event_or_run_obj.__aiter__()
                first = await ait.__anext__()  # may raise StopAsyncIteration
                rid = getattr(first, "id", None)
                if rid:
                    self.logger.debug(f"[extract_run_id] Extracted '{rid}' from first event")
                    return rid

            self.logger.warning(f"[extract_run_id] Could not extract run ID (thread='{thread_id}')")
            return None
        except Exception as e:
            self.logger.error(f"[extract_run_id] Error: {e}", exc_info=True)
            return None
