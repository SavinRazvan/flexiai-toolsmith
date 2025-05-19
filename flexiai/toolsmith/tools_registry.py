# FILE: flexiai/toolsmith/tools_registry.py

"""
tools_registry module.

Handles registration and execution of agent tools for FlexiAI.
Maintains a unified mapping of core and custom tools.
"""

from __future__ import annotations
import logging
from typing import Any, Callable, Dict

from flexiai.toolsmith.tools_manager import ToolsManager


class RegistryError(Exception):
    """Raised when the ToolsRegistry fails to perform an operation."""
    pass


class ToolsRegistry:
    """
    Registry for mapping tool names to callables for FlexiAI agents.

    Attributes:
        core_tool_manager: Provides implementations of core agent tools.
        registered_tools: Maps tool names to their callables.
    """

    def __init__(self, core_tool_manager: ToolsManager) -> None:
        """
        Initialize the ToolsRegistry and populate it exactly once.
        """
        self.logger = logging.getLogger(__name__)
        self.core_tool_manager = core_tool_manager
        self.registered_tools: Dict[str, Callable[..., Any]] = {}
        self._initialized = False
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """
        Internal: populate registry only on first invocation.
        """
        if self._initialized:
            return

        self.logger.info("Initializing tool registry…")
        try:
            self.map_core_tools()
            self.map_custom_tools()
            self.logger.info("Tool registry initialized successfully.")
            self._initialized = True
        except Exception as e:
            self.logger.error("Failed to initialize tool registry.", exc_info=True)
            raise RegistryError from e

    def map_core_tools(self) -> None:
        """
        Register core agent tools from the ToolsManager into the registry.

        Raises:
            RegistryError: If mapping of core tools fails.
        """
        self.logger.info("Mapping core tools into registry…")
        try:
            core_tools: Dict[str, Callable[..., Any]] = {
                # Dynamic MAS
                "save_processed_content":     self.core_tool_manager.save_processed_content,
                "load_processed_content":     self.core_tool_manager.load_processed_content,
                "initialize_agent":           self.core_tool_manager.initialize_agent,
                "communicate_with_assistant": self.core_tool_manager.communicate_with_assistant,

                # Mixed for WEB tests
                "search_youtube":             self.core_tool_manager.search_youtube,
                # "ai_custom_products":         self.core_tool_manager.filter_products,
                "search_on_youtube":          self.core_tool_manager.search_on_youtube,
                
                # Custom CSV
                "identify_subscriber":        self.core_tool_manager.identify_subscriber,
                "retrieve_billing_details":   self.core_tool_manager.retrieve_billing_details,
                "manage_services":            self.core_tool_manager.manage_services,

                # Infrastructure: Spreadsheet
                "file_operations":            self.core_tool_manager.file_operations,
                "sheet_operations":           self.core_tool_manager.sheet_operations,
                "data_entry_operations":      self.core_tool_manager.data_entry_operations,
                "data_retrieval_operations":  self.core_tool_manager.data_retrieval_operations,
                "data_analysis_operations":   self.core_tool_manager.data_analysis_operations,
                "formula_operations":         self.core_tool_manager.formula_operations,
                "formatting_operations":      self.core_tool_manager.formatting_operations,
                "data_validation_operations": self.core_tool_manager.data_validation_operations,
                "data_transformation_operations": self.core_tool_manager.data_transformation_operations,
                "chart_operations":           self.core_tool_manager.chart_operations,

                # Infrastructure: CSV
                "csv_operations":             self.core_tool_manager.csv_operations,
                
                # Security Audit
                "security_audit":             self.core_tool_manager.security_audit,
            }
            self.registered_tools.update(core_tools)
            self.logger.info("Mapped core tools: %s", list(core_tools.keys()))
        except Exception:
            self.logger.error("Error mapping core tools.", exc_info=True)
            raise RegistryError from None

    def map_custom_tools(self) -> None:
        """
        Register user-defined/custom tools into the registry.

        Note:
            No custom tools are registered by default.
        """
        self.logger.info("No custom tools found; using core tools only.")

    def refresh_tool_mappings(self) -> None:
        """
        Clear and rebuild all tool mappings from scratch.

        Raises:
            RegistryError: If refreshing tool mappings fails.
        """
        self.logger.info("Refreshing tool mappings…")
        try:
            self.registered_tools.clear()
            # reset guard so we can re-run initialization if desired
            self._initialized = False
            self._initialize_registry()
            self.logger.info("Tool mappings refreshed successfully.")
        except Exception:
            self.logger.error("Failed to refresh tool mappings.", exc_info=True)
            raise RegistryError from None

    def get_all_tools(self) -> Dict[str, Callable[..., Any]]:
        """
        Retrieve the full mapping of registered tools.

        Returns:
            A shallow copy of the tool-name to callable mapping.
        """
        return dict(self.registered_tools)
