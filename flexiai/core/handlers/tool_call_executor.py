# FILE: flexiai/core/handlers/tool_call_executor.py

"""
ToolCallExecutor module.

Executes registered tool functions (agent_actions) and formats their outputs
for submission back to the AI run.
"""

from __future__ import annotations
import json
import logging
from typing import Any, Dict, Callable
from flexiai.utils.context_utils import return_context


class ToolCallExecutor:
    """Executes tool calls and prepares their outputs for the AI service."""

    def __init__(self, agent_actions: Dict[str, Callable[..., Any]]) -> None:
        """
        Initialize the executor.

        Args:
            agent_actions (Dict[str, Callable[..., Any]]): Mapping of tool names to callables.
            logger (Any): Logger instance for diagnostics.
        """
        self.agent_actions = agent_actions
        self.logger = logging.getLogger(__name__)

    def execute(self, tool_name: str, **arguments: Any) -> Any:
        """
        Execute a tool action by name.

        Args:
            tool_name (str): The key in agent_actions.
            **arguments: Keyword arguments to pass to the tool.

        Returns:
            Any: The return value of the tool function.

        Raises:
            ValueError: If the tool_name is not registered.
            Exception: If the tool call itself raises.
        """
        self.logger.info(f"[execute] Running '{tool_name}' with {arguments}")
        action = self.agent_actions.get(tool_name)
        if action is None:
            self.logger.error(f"[execute] Unknown tool '{tool_name}'")
            raise ValueError(f"Tool '{tool_name}' not found")
        try:
            result = action(**arguments)
            self.logger.debug(f"[execute] '{tool_name}' succeeded")
            return result
        except Exception as e:
            self.logger.error(f"[execute] Error in '{tool_name}': {e}", exc_info=True)
            raise

    def prepare_tool_output(self, tool_call: Any, result: Any, success: bool = True) -> Dict[str, Any]:
        """
        Format and truncate the result of a tool call for API submission.

        Applies return_context to the serialized JSON payload to ensure
        it does not exceed the model's token limit.

        Args:
            tool_call (Any): Original tool call object (with .id attribute).
            result (Any): The result returned by execute().
            success (bool): True if execution succeeded.

        Returns:
            Dict[str, Any]: {
                "tool_call_id": str,
                "output": str  # JSON string, possibly truncated to fit context
            }
        """
        call_id = getattr(tool_call, "id", "Unknown ID")

        if success:
            payload = {"status": True, "message": "Success", "result": result}
        else:
            payload = {"status": False, "message": str(result), "result": None}

        # Serialize to JSON
        raw_json = json.dumps(payload, ensure_ascii=False)
        # Truncate to model context window
        truncated = return_context(raw_json)

        self.logger.debug(
            f"[prepare_tool_output] call_id='{call_id}', success={success}, "
            f"original_len={len(raw_json)}, truncated_len={len(truncated)}"
        )

        return {"tool_call_id": call_id, "output": truncated}

    def track_tool_call_event(self, tool_call_id: str, status: str, thread_id: str, run_id: str) -> None:
        """
        Log a lifecycle event for a tool call.

        Args:
            tool_call_id (str): Identifier for the tool call.
            status (str): One of "Pending", "Completed", "Submitted", "Failed".
            thread_id (str): Associated thread ID.
            run_id (str): Associated run ID.
        """
        self.logger.info(
            f"[track_tool_call_event] Call '{tool_call_id}' status '{status}' | "
            f"Thread='{thread_id}', Run='{run_id}'"
        )

    def process_tool_call(
        self,
        tool_call_id: str,
        thread_id: str,
        run_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> None:
        """
        Execute a tool call end-to-end and submit its output.

        Args:
            tool_call_id (str): Unique ID for the tool call.
            thread_id (str): Thread ID for context.
            run_id (str): Run ID for context.
            tool_name (str): Registered tool/action name.
            arguments (Dict[str, Any]): Parameters for the tool.
        """
        self.track_tool_call_event(tool_call_id, "Pending", thread_id, run_id)
        try:
            result = self.execute(tool_name, **arguments)
            self.track_tool_call_event(tool_call_id, "Completed", thread_id, run_id)
            output = self.prepare_tool_output(tool_call=tool_call_id, result=result, success=True)
            self.logger.info(f"[process_tool_call] Submitting output for '{tool_call_id}'")
            # Here you would call submit_tool_outputs or similar
            self.track_tool_call_event(tool_call_id, "Submitted", thread_id, run_id)
        except Exception as e:
            self.track_tool_call_event(tool_call_id, "Failed", thread_id, run_id)
            self.logger.error(f"[process_tool_call] Error in '{tool_call_id}': {e}", exc_info=True)
