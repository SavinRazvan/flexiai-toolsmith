# FILE: flexiai/core/handlers/event_handler.py

"""
Event handling module for FlexiAI.

Defines EventHandler, which processes streaming events from the AI service,
dispatches them to appropriate handlers, manages tool calls, and publishes
events to configured channels.
"""

from __future__ import annotations
import json
import logging
import asyncio
from typing import Any, Optional, Dict, Callable

from flexiai.core.handlers.tool_call_executor import ToolCallExecutor
from flexiai.core.handlers.run_thread_manager import RunThreadManager
from flexiai.core.handlers.event_dispatcher import EventDispatcher
from flexiai.core.events.event_models import MessageDeltaEvent
from flexiai.channels.multi_channel_publisher import MultiChannelPublisher

from flexiai.core.events.rolling_event_buffer import RollingEventBuffer
from flexiai.core.events.session import ChatSession
from flexiai.controllers.quart_chat_controller import QuartChatController

class EventHandler:
    """Processes AI service events and orchestrates their handling and publication."""

    def __init__(
        self,
        client: Any,
        assistant_id: str,
        run_thread_manager: RunThreadManager,
        agent_actions: Dict[str, Callable[..., Any]],
        event_dispatcher: Optional[EventDispatcher] = None
    ) -> None:
        """Initialize the EventHandler with dependencies."""
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.assistant_id = assistant_id
        self.run_thread_manager = run_thread_manager
        # Attach or create the dispatcher
        self.event_dispatcher = event_dispatcher or EventDispatcher(self)
        self.tool_call_executor = ToolCallExecutor(agent_actions=agent_actions)
        self.logger.info(f"[EventHandler] Initialized for assistant '{assistant_id}'.")
        # Will be set by controller before each run
        self.event_queue: asyncio.Queue[dict] | None = None
        # Carry the end-user's ID across event callbacks
        self.current_user_id: Optional[str] = None

    async def start_run(
        self,
        assistant_id: str,
        thread_id: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Begin an assistant run by consuming the async stream of events
        directly on the event loop.

        Args:
            assistant_id (str): Assistant identifier.
            thread_id (str): Thread identifier.
            user_id (Optional[str]): Unique identifier of the end user.
        """
        self.logger.info(f"[start_run] assistant='{assistant_id}', thread='{thread_id}', user='{user_id}'")
        # Store for use in delta and completed handlers
        self.current_user_id = user_id

        try:
            run_stream = await self.run_thread_manager.start_run(assistant_id, thread_id)
            async for event in run_stream:
                evt_tid = getattr(event, "thread_id", thread_id)
                if not self._validate_thread(evt_tid, thread_id, assistant_id):
                    continue
                etype = getattr(event, "event", None)
                self.event_dispatcher.dispatch(etype, event, thread_id)
        except Exception as e:
            self.logger.error(f"[start_run] Error during run: {e}", exc_info=True)

    def _handle_run_requires_action(self, event_data: Any, thread_id: str) -> None:
        """Handle run requiring action (tool calls)."""
        if not self._validate_thread(
            getattr(event_data.data, "thread_id", None),
            thread_id,
            self.assistant_id
        ):
            return

        self.logger.info(f"[_handle_run_requires_action] Requires action in thread '{thread_id}'.")
        asyncio.create_task(self._handle_requires_action(event_data, thread_id))

    async def _handle_requires_action(self, run_data: Any, thread_id: str) -> None:
        """Execute required tool calls and submit their outputs asynchronously."""
        required = getattr(run_data.data, "required_action", None)
        if not required or not getattr(required, "submit_tool_outputs", None):
            self.logger.warning("[_handle_requires_action] No tool calls.")
            return

        tool_calls = required.submit_tool_outputs.tool_calls
        run_id = getattr(run_data.data, "id", "Unknown Run ID")
        outputs: list[Dict[str, Any]] = []

        for tc in tool_calls:
            tc_id = getattr(tc, "id", "Unknown Tool Call ID")
            func = getattr(tc, "function", None)
            name = getattr(func, "name", "Unknown Function")
            try:
                args = json.loads(getattr(func, "arguments", "{}"))
            except Exception:
                self.logger.error(f"[_handle_requires_action] Bad JSON for '{tc_id}'", exc_info=True)
                args = {}

            self.track_tool_call_event(tc_id, "Pending", thread_id, run_id, function_name=name)
            try:
                result = self.tool_call_executor.execute(name, **args)
                self.track_tool_call_event(tc_id, "Completed", thread_id, run_id, function_name=name)
                success = True
            except Exception as e:
                result = str(e)
                self.track_tool_call_event(tc_id, "Failed", thread_id, run_id, function_name=name)
                success = False

            try:
                out = self.tool_call_executor.prepare_tool_output(
                    tool_call=tc, result=result, success=success
                )
                outputs.append(out)
            except Exception as e:
                self.logger.error(
                    f"[_handle_requires_action] Prep output failed for '{tc_id}': {e}", exc_info=True
                )

        try:
            mgr = self.run_thread_manager.submit_tool_outputs_stream(thread_id, run_id, outputs)
            async with mgr as stream:
                async for ev in stream:
                    et = getattr(ev, "event", None)
                    self.event_dispatcher.dispatch(et, ev, thread_id)
        except Exception as e:
            self.logger.error(f"[_handle_requires_action] Submission error: {e}", exc_info=True)

    def _validate_thread(
        self,
        event_thread_id: Optional[str],
        expected_thread_id: str,
        assistant_id: str
    ) -> bool:
        """Ensure the event belongs to the correct thread for this assistant+user."""
        if event_thread_id is None:
            event_thread_id = expected_thread_id

        if event_thread_id != expected_thread_id:
            self.logger.warning(
                "[_validate_thread] Thread mismatch. Event: '%s', Expected: '%s'. Ignoring.",
                event_thread_id, expected_thread_id
            )
            return False

        info = self.run_thread_manager.track_assistant_in_thread(assistant_id, self.current_user_id)
        if not info or info.get("thread_id") != event_thread_id:
            self.logger.error(
                "[_validate_thread] Thread '%s' not associated with assistant '%s' (user '%s'). Ignoring.",
                event_thread_id, assistant_id, self.current_user_id
            )
            return False

        return True

    # --- Event Handlers ---

    def _handle_thread_created(self, event_data: Any, thread_id: str) -> None:
        tid = getattr(event_data, "id", "No ID")
        self.logger.info(f"[_handle_thread_created] Thread created: '{tid}'.")

    def _handle_run_created(self, event_data: Any, thread_id: str) -> None:
        run_id = getattr(event_data.data, "id", "No ID")
        if not self._validate_thread(
            getattr(event_data.data, "thread_id", None),
            thread_id,
            self.assistant_id
        ):
            return
        self.logger.info(f"[_handle_run_created] Run '{run_id}' created for thread '{thread_id}'.")

    def _handle_run_queued(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_queued] Run queued for thread '{thread_id}'.")

    def _handle_run_in_progress(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_in_progress] Run in progress for thread '{thread_id}'.")

    def _handle_run_completed(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_completed] Run completed for thread '{thread_id}'.")
        # carry user_id through
        data_with_user = getattr(event_data.data, "__dict__", {}) if hasattr(event_data.data, "__dict__") else dict(event_data.data)
        data_with_user["user_id"] = self.current_user_id
        term_event = {
            "event_type": "thread.run.completed",
            "data": data_with_user
        }
        MultiChannelPublisher().publish("thread.run.completed", term_event)
        self.event_queue.put_nowait(term_event)

    def _handle_run_incomplete(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_incomplete] Run incomplete for thread '{thread_id}'.")

    def _handle_run_failed(self, event_data: Any, thread_id: str) -> None:
        self.logger.error(f"[_handle_run_failed] Run failed for thread '{thread_id}'.")

    def _handle_run_cancelling(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_cancelling] Run cancelling for thread '{thread_id}'.")

    def _handle_run_cancelled(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_cancelled] Run cancelled for thread '{thread_id}'.")

    def _handle_run_expired(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_expired] Run expired for thread '{thread_id}'.")

    def _handle_run_step_created(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_step_created] Step created in thread '{thread_id}'.")

    def _handle_run_step_in_progress(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_step_in_progress] Step in progress in thread '{thread_id}'.")

    def _handle_run_step_delta(self, event_data: Any, thread_id: str) -> None:
        if hasattr(event_data, "data") and hasattr(event_data.data, "delta"):
            self._handle_delta(event_data.data.delta, snapshot=event_data.data)
        else:
            self.logger.warning("[_handle_run_step_delta] Missing data.delta.")

    def _handle_run_step_completed(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_step_completed] Step completed in thread '{thread_id}'.")

    def _handle_run_step_failed(self, event_data: Any, thread_id: str) -> None:
        self.logger.error(f"[_handle_run_step_failed] Step failed in thread '{thread_id}'.")

    def _handle_run_step_cancelled(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_step_cancelled] Step cancelled in thread '{thread_id}'.")

    def _handle_run_step_expired(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_run_step_expired] Step expired in thread '{thread_id}'.")

    def _handle_message_created(self, event_data: Any, thread_id: str) -> None:
        mid = getattr(event_data.data, "id", "No ID")
        self.logger.info(f"[_handle_message_created] Message '{mid}' created in thread '{thread_id}'.")


    def _handle_message_delta(self, event_data: Any, thread_id: str) -> None:
        """Handle message delta (streaming content) event."""
        try:
            snapshot = event_data.data
            delta = getattr(snapshot, "delta", None)
            if not delta:
                self.logger.warning("[_handle_message_delta] Missing delta.")
                return

            user = getattr(snapshot, "user_id", None) or self.current_user_id or "unknown"
            for block in getattr(delta, "content", []):
                if block.type == "text" and hasattr(block.text, "value"):
                    chunk = block.text.value
                    evt = MessageDeltaEvent(
                        event_type="message_delta",
                        data={"user_id": user},
                        message_id=getattr(snapshot, "id", "No ID"),
                        content=[chunk]
                    )
                    MultiChannelPublisher().publish("message_delta", evt)
                else:
                    self.logger.warning("[_handle_message_delta] Non-text block.")
        except Exception as e:
            self.logger.error(f"[_handle_message_delta] Error: {e}", exc_info=True)

    def _handle_message_completed(self, event_data: Any, thread_id: str) -> None:
        mid = getattr(event_data.data, "id", "No ID")
        self.logger.info(f"[_handle_message_completed] Message '{mid}' completed in thread '{thread_id}'.")
        data_with_user = getattr(event_data.data, "__dict__", {}) if hasattr(event_data.data, "__dict__") else dict(event_data.data)
        data_with_user["user_id"] = self.current_user_id
        evt = {
            "event_type": "message_completed",
            "data": data_with_user
        }
        MultiChannelPublisher().publish("message_completed", evt)
        self.event_queue.put_nowait(evt)


    def _handle_message_in_progress(self, event_data: Any, thread_id: str) -> None:
        mid = getattr(event_data.data, "id", "No ID")
        self.logger.info(f"[_handle_message_in_progress] Message '{mid}' in progress in thread '{thread_id}'.")

    def _handle_message_incomplete(self, event_data: Any, thread_id: str) -> None:
        self.logger.warning(f"[_handle_message_incomplete] Incomplete in thread '{thread_id}'.")

    def _handle_error_event(self, event_data: Any, thread_id: str) -> None:
        self.logger.error(f"[_handle_error_event] Error in thread '{thread_id}': {event_data}")

    def _handle_done_event(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_done_event] Done in thread '{thread_id}'.")
        evt = {"event_type": "done", "data": {"user_id": self.current_user_id}}
        self.event_queue.put_nowait(evt)

    def _handle_unhandled_event(self, event_data: Any, thread_id: str) -> None:
        self.logger.info(f"[_handle_unhandled_event] Unhandled event in thread '{thread_id}': {event_data}")

    def track_tool_call_event(
        self,
        tool_call_id: str,
        status: str,
        thread_id: str,
        run_id: str,
        step_id: Optional[str] = None,
        tool_call_type: Optional[str] = None,
        function_name: Optional[str] = None
    ) -> None:
        """Log lifecycle events for tool calls."""
        msg = (
            f"[track_tool_call_event] Thread '{thread_id}', Call '{tool_call_id}': "
            f"Status '{status}', Run '{run_id}', Step '{step_id}'"
        )
        if tool_call_type:
            msg += f", Type '{tool_call_type}'"
        if function_name:
            msg += f", Function '{function_name}'"
        self.logger.info(msg)

    def _handle_delta(self, delta: Any, snapshot: Any) -> None:
        """Publish text deltas for tool calls or assistant messages."""
        try:
            user = getattr(snapshot, "user_id", None) or self.current_user_id or "unknown"
            # Tool-call output delta
            if hasattr(delta, "tool_call_id") or (
                hasattr(delta, "function") and getattr(delta.function, "output", None)
            ):
                tc_id = getattr(delta, "tool_call_id", getattr(delta, "id", "Unknown"))
                func = getattr(delta, "function", None)
                text = getattr(func, "output", "") or getattr(func, "arguments", "")
                if text.strip():
                    self.logger.debug(
                        f"[_handle_delta] Tool call delta chunk: '{text[:150]}'... (len={len(text)})"
                    )
                    evt = MessageDeltaEvent(
                        event_type="tool_call_delta",
                        data={"user_id": user},
                        message_id=tc_id,
                        content=[text]
                    )
                    MultiChannelPublisher().publish("tool_call_delta", evt)
            else:
                # Regular assistant message delta
                content_blocks = getattr(delta, "content", [])
                text = "".join(
                    block.text.value
                    for block in content_blocks
                    if block.type == "text" and hasattr(block.text, "value")
                )
                if text:
                    self.logger.debug(
                        f"[_handle_delta] Assistant delta chunk: '{text[:30]}'... (len={len(text)})"
                    )
                    evt = MessageDeltaEvent(
                        event_type="message_delta",
                        data={"user_id": user},
                        message_id=getattr(snapshot, "id", ""),
                        content=[text]
                    )
                    MultiChannelPublisher().publish("message_delta", evt)
        except Exception as e:
            self.logger.error(f"[_handle_delta] Error: {e}", exc_info=True)
