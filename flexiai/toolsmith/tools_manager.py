# FILE: flexiai/toolsmith/tools_manager.py

"""
tools_manager module.

Defines ToolsManager, responsible for core system operations exposed as tools:
- Saving and loading processed content for retrieval-augmented generation (RAG).
- Initializing agents and managing their threads.
- Facilitating inter-assistant communication.
- Executing external tool calls (e.g., YouTube search).
- Filtering products data.
- Dispatching spreadsheet and CSV operations.
- Identifying subscribers and managing services.
- Performing system security audits.
"""

from __future__ import annotations
import logging
import threading
import subprocess
import os
import urllib
import json
from typing import Any, Dict, Tuple, List, Optional, Union, TYPE_CHECKING

from dotenv import load_dotenv
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError

# load only once, at module import (experiment 1)
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


from flexiai.core.handlers.run_thread_manager import RunThreadManager
from flexiai.toolsmith.tools_infrastructure.csv_helpers import CSVHelpers
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.mixed_helpers import prepare_tool_output
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.spreadsheet_entrypoint import (
    file_operations, sheet_operations, data_entry_operations, data_retrieval_operations,
    data_analysis_operations, formula_operations, formatting_operations,
    data_validation_operations, data_transformation_operations,
)
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.csv_entrypoint import csv_entrypoint
from flexiai.toolsmith.tools_infrastructure.security_audit import SecurityAudit, security_audit_dispatcher

if TYPE_CHECKING:
    from flexiai.core.handlers.event_handler import EventHandler
    from flexiai.toolsmith.tools_registry import ToolsRegistry


class ToolsManager:
    """
    Manages core system operations for FlexiAI exposed as tools.
    """

    def __init__(
        self,
        client: Any,
        run_thread_manager: RunThreadManager,
        tools_registry: Optional[ToolsRegistry] = None,
        event_handler: Optional[EventHandler] = None,
    ) -> None:
        """
        Initialize ToolsManager.

        Args:
            client: AI service client for backend interactions.
            run_thread_manager: Manages threads, runs, and messages.
            tools_registry: Optional ToolsRegistry; if None, one will be created.
            event_handler: Optional default EventHandler.
        """
        self.client = client
        self.run_thread_manager = run_thread_manager
        self.event_handler = event_handler
        self.logger = logging.getLogger(__name__)

        if tools_registry is None:
            self.logger.info("[ToolsManager] No tools_registry provided; creating one.")
            from flexiai.toolsmith.tools_registry import ToolsRegistry
            tools_registry = ToolsRegistry(self)

        self.tools_registry = tools_registry

        # Map (from_assistant, to_assistant) -> list of processed content strings
        self.processed_content_map: Dict[Tuple[str, str], List[str]] = {}
        self.lock = threading.Lock()

        # For product filtering
        self.filtered_products: List[Dict[str, Any]] = []
        self.products_version: int = 0

        # CSV and spreadsheet helpers
        self.csv_helpers = CSVHelpers()
        
        # Core SecurityAudit instance
        self._security_audit = SecurityAudit()


    def security_audit(
        self,
        operation: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Dispatch a SecurityAudit operation to collect structured data.

        Supported operations and their structured results:

          - reconnaissance
            • No args  
            • result: {
                "connections": [ {proto, local, remote, state}, … ],
                "neighbors":   [ {ip, mac, state}, … ]
              }

          - detect_processes
            • No args  
            • result: { "processes": [ {pid, user, name}, … ] }

          - port_scan
            • target (str)        – hostname or IP to scan  
            • start_port (int)    – optional, default=1  
            • end_port (int)      – optional, default=1024  
            • result: {
                "target": str,
                "range": [int, int],
                "open_ports": [int, …],
                "total_open": int
              }

          - network_scan
            • network (str)       – required, network CIDR (e.g., "192.168.1.0/24")  
            • result: {
                "network": str,
                "alive_hosts": [str,…],
                "total_alive": int
              }

          - defense_actions
            • bad_ips (List[str])  – optional  
            • bad_pids (List[int]) – optional  
            • bad_ports (List[int])– optional  
            • result: {
                "blocked_ips":   [str,…],
                "killed_pids":   [int,…],
                "blocked_ports": [int,…],
                "errors":        [str,…]
              }

          - update_system
            • No args  
            • result: {
                "ran_as":  "windows"|"root"|"non-root",
                "skipped": bool?,
                "commands": [str,…]       # for Linux
              }

        Args:
            operation: One of the above operations.
            **kwargs: Parameters for that operation.

        Returns:
            A dict with:
              - status (bool): success flag  
              - message (str): human-readable summary  
              - result (dict|null): structured data as described per operation
        """
        try:
            return security_audit_dispatcher(operation, **kwargs)
        except Exception as e:
            self.logger.error(f"[security_audit] unexpected error calling {operation}: {e}", exc_info=True)
            return {"status": False, "message": str(e), "result": None}


    def initialize_agent(self, assistant_id: str) -> str:
        """
        Ensure a thread exists and start a non‑streaming run to initialize an assistant.

        Args:
            assistant_id: The assistant's unique identifier.

        Returns:
            A status message indicating success or failure.
        """
        self.logger.info(f"[initialize_agent] Initializing assistant '{assistant_id}'.")
        try:
            thread_id = self.run_thread_manager.get_or_create_thread(assistant_id)
            self.logger.debug(f"[initialize_agent] Obtained thread '{thread_id}' for assistant '{assistant_id}'.")

            from flexiai.core.handlers.event_handler import EventHandler
            handler = EventHandler(
                client=self.client,
                logger=self.logger,
                assistant_id=assistant_id,
                run_thread_manager=self.run_thread_manager,
                agent_actions=self.tools_registry.get_all_tools()
            )
            self.logger.debug(f"[initialize_agent] EventHandler created for assistant '{assistant_id}'.")

            # Send a system message
            self.run_thread_manager.add_message_to_thread(thread_id, "Agent initialized successfully.")
            self.logger.debug(f"[initialize_agent] System message added to thread '{thread_id}'.")

            # Perform a non‑streaming run
            handler.start_run(assistant_id, thread_id)
            self.logger.info(f"[initialize_agent] Assistant '{assistant_id}' initialized.")
            return f"Assistant '{assistant_id}' initialized successfully."
        except Exception as e:
            msg = f"[initialize_agent] Error initializing assistant '{assistant_id}': {e}"
            self.logger.error(msg, exc_info=True)
            return msg


    def communicate_with_assistant(self, assistant_id: str, user_content: str) -> str:
        """
        Send a message to another assistant synchronously.

        Args:
            assistant_id: Target assistant's ID.
            user_content: Message content to send.

        Returns:
            A status message indicating success or failure.
        """
        self.logger.info(f"[communicate_with_assistant] Messaging assistant '{assistant_id}'.")
        try:
            thread_id = self.run_thread_manager.get_or_create_thread(assistant_id)
            self.logger.debug(f"[communicate_with_assistant] Thread '{thread_id}' ready for assistant '{assistant_id}'.")

            from flexiai.core.handlers.event_handler import EventHandler
            handler = EventHandler(
                client=self.client,
                logger=self.logger,
                assistant_id=assistant_id,
                run_thread_manager=self.run_thread_manager,
                agent_actions=self.tools_registry.get_all_tools()
            )

            self.run_thread_manager.add_message_to_thread(thread_id, user_content)
            self.logger.debug(f"[communicate_with_assistant] Added user message to thread '{thread_id}'.")

            handler.start_run(assistant_id, thread_id)
            self.logger.info(f"[communicate_with_assistant] Message sent to assistant '{assistant_id}'.")
            return f"Message successfully sent to assistant '{assistant_id}'."
        except Exception as e:
            msg = f"[communicate_with_assistant] Error sending message: {e}"
            self.logger.error(msg, exc_info=True)
            return msg


    def save_processed_content(self, from_assistant_id: str, to_assistant_id: str, processed_content: str) -> bool:
        """
        Save processed content for retrieval-augmented generation.

        Args:
            from_assistant_id: Source assistant ID.
            to_assistant_id: Target assistant ID.
            processed_content: Content to save.

        Returns:
            True if saved successfully; False otherwise.
        """
        self.logger.info(f"[save_processed_content] From '{from_assistant_id}' to '{to_assistant_id}'.")
        if not all([from_assistant_id, to_assistant_id, processed_content]):
            self.logger.error("[save_processed_content] Invalid inputs; aborting.")
            return False
        try:
            with self.lock:
                key = (from_assistant_id, to_assistant_id)
                self.processed_content_map.setdefault(key, []).append(processed_content)
            self.logger.info("[save_processed_content] Content saved.")
            return True
        except Exception as e:
            self.logger.error(f"[save_processed_content] Error: {e}", exc_info=True)
            return False


    def load_processed_content(
        self,
        from_assistant_id: str,
        to_assistant_id: str,
        multiple_retrieval: bool = False
    ) -> List[str]:
        """
        Load previously saved processed content.

        Args:
            from_assistant_id: Source assistant ID.
            to_assistant_id: Target assistant ID.
            multiple_retrieval: If True, return all contents for to_assistant_id.

        Returns:
            List of content strings.
        """
        self.logger.info(f"[load_processed_content] Loading for '{to_assistant_id}' from '{from_assistant_id}'.")
        try:
            with self.lock:
                if multiple_retrieval:
                    return [
                        content
                        for (frm, to), contents in self.processed_content_map.items()
                        if to == to_assistant_id
                        for content in contents
                    ]
                else:
                    return self.processed_content_map.pop((from_assistant_id, to_assistant_id), [])
        except Exception as e:
            self.logger.error(f"[load_processed_content] Error: {e}", exc_info=True)
            return []


    def search_youtube(self, query: str) -> dict:
        """
        Open a YouTube search in the default browser.

        Args:
            query: Search terms.

        Returns:
            Dict with status, message, and result URL.
        """
        self.logger.info(f"[search_youtube] Query: {query}")
        if not query:
            return {"status": False, "message": "Query cannot be empty.", "result": None}
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded}"
            subprocess.run(
                ["cmd.exe", "/c", "start", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return {"status": True, "message": "YouTube search page opened.", "result": url}
        except Exception as e:
            self.logger.error(f"[search_youtube] Error: {e}", exc_info=True)
            return {"status": False, "message": str(e), "result": None}


    def search_on_youtube(self, query: str, links_nr: int = 1) -> Dict[str, Any]:
        """
        Search YouTube for the given query and build embeddable HTML snippets
        for the top `links_nr` videos.

        Args:
            query: Search terms.
            links_nr: Number of top video results to fetch (default: 3).

        Returns:
            {
                "status": bool,
                "message": str,
                "result": {
                    "search_url": str,
                    "embeds": [ str, ... ]  # HTML strings ready to render
                }
            }
        """
        if not query:
            return {"status": False, "message": "Query cannot be empty.", "result": None}

        if not YOUTUBE_API_KEY:
            return {
                "status": False,
                "message": "YouTube API key not configured. Set YOUTUBE_API_KEY in your .env.",
                "result": None
            }

        try:
            # Initialize YouTube client
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

            # Perform search for video IDs
            search_response = (
                youtube.search()
                    .list(q=query, part="id", type="video", maxResults=links_nr)
                    .execute()
            )
            items = search_response.get("items", [])
            video_ids = [item["id"]["videoId"] for item in items if item["id"].get("videoId")]

            # Build a standard YouTube search URL (for reference)
            encoded = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded}"

            # Build embeddable HTML snippets for each video
            embeds: List[str] = []
            for vid in video_ids:
                embeds.append(
                    f'<div class="hero-video">'
                    f'  <iframe '
                    f'src="https://www.youtube.com/embed/{vid}" '
                    f'allowfullscreen '
                    f'frameborder="0" '
                    f'scrolling="no">'
                    f'</iframe>'
                    f'</div>'
                )

            return {
                "status": True,
                "message": f"Found top {len(embeds)} videos for “{query}.”",
                "result": {
                    "search_url": search_url,
                    "embeds": embeds
                }
            }

        except HttpError as e:
            self.logger.error(f"[search_on_youtube] YouTube API error: {e}")
            return {"status": False, "message": str(e), "result": None}
        except Exception as e:
            self.logger.error(f"[search_on_youtube] Unexpected error: {e}", exc_info=True)
            return {"status": False, "message": str(e), "result": None}


    def filter_products(
        self,
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        quantity: Optional[int] = None,
        price: Optional[Union[int, float, List[Union[int, float]]]] = None,
        discount: Optional[Union[int, float, List[Union[int, float]]]] = None,
        color: Optional[str] = None,
        category: Optional[str] = None,
        number_of_products_displayed: int = 16
    ) -> Dict[str, Any]:
        """
        Filter products from 'products.json' by various criteria.

        Always updates self.filtered_products and increments version.

        Args:
            product_id: Exact ID to match.
            product_name: Substring to search in product_name.
            description: Substring to search in description.
            quantity: Exact quantity match.
            price: Single value or [min, max] range.
            discount: Single value or [min, max] range.
            color: Substring to search in colors list or color field.
            category: Exact category match.
            number_of_products_displayed: Maximum results to return.

        Returns:
            Dict with 'status', 'message', and 'result' (list of products).
        """
        self.logger.info(f"[filter_products] Params: id={product_id}, name={product_name}, price={price}, discount={discount}, color={color}, category={category}")
        path = os.path.join(os.getcwd(), "products.json")
        try:
            with open(path, "r") as f:
                all_products = json.load(f)
        except Exception as e:
            msg = f"Failed to load products.json: {e}"
            self.logger.error(f"[filter_products] {msg}", exc_info=True)
            return {"status": False, "message": msg, "result": []}

        filtered: List[dict] = []
        for prod in all_products:
            if product_id is not None and prod.get("id") != product_id:
                continue
            if product_name and product_name.lower() not in prod.get("product_name", "").lower():
                continue
            if description and description.lower() not in prod.get("description", "").lower():
                continue
            if quantity is not None and prod.get("quantity") != quantity:
                continue
            if price is not None:
                if isinstance(price, list):
                    lo, hi = (price[0], price[0]) if len(price) == 1 else (price[0], price[1])
                    if not (lo <= prod.get("price", 0) <= hi):
                        continue
                elif prod.get("price") != price:
                    continue
            if discount is not None:
                if isinstance(discount, list):
                    lo, hi = (discount[0], discount[0]) if len(discount) == 1 else (discount[0], discount[1])
                    if not (lo <= prod.get("discount", 0) <= hi):
                        continue
                elif prod.get("discount") != discount:
                    continue
            if color:
                cols = prod.get("colors") or [prod.get("color", "")]
                if not any(color.lower() in c.lower() for c in cols):
                    continue
            if category and prod.get("category", "").lower() != category.lower():
                continue
            filtered.append(prod)

        self.filtered_products = filtered[:number_of_products_displayed]
        self.products_version += 1
        self.logger.info(f"[filter_products] {len(self.filtered_products)} products matched; version={self.products_version}")
        return {"status": True, "message": "Filtered products retrieved.", "result": self.filtered_products}


    def file_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
    ) -> Dict[str, Any]:
        """
        Extends the functionality of file_operations dispatcher.
        """
        self.logger.info(
            f"[file_operations] operation='{operation}', path='{path}', file_name='{file_name}'"
        )
        try:
            result = file_operations(operation, path=path, file_name=file_name)
            serialized = prepare_tool_output(result)
            return serialized
        except Exception as e:
            self.logger.error(f"[file_operations] Error: {e}", exc_info=True)
            raise


    def sheet_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        new_sheet_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extends the functionality of sheet_operations dispatcher.
        """
        self.logger.info(
            f"[sheet_operations] operation='{operation}', file='{file_name}', sheet='{sheet_name}', new_sheet_name='{new_sheet_name}'"
        )
        try:
            result = sheet_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                new_sheet_name=new_sheet_name,
            )
            serialized = prepare_tool_output(result)
            return serialized
        except Exception as e:
            self.logger.error(f"[sheet_operations] Error: {e}", exc_info=True)
            raise


    def data_entry_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        data: Optional[List[str]] = None,
        rows: Optional[List[List[str]]] = None,
        headers: Optional[List[str]] = None,
        row_id: Optional[str] = None,
        column_name: Optional[str] = None,
        new_data: Optional[List[str]] = None,
        skip_header: bool = True,
        has_headers: bool = True
    ) -> Dict[str, Any]:
        """
        Extends data entry operations (add_row, delete_row, etc.).
        """
        self.logger.info(
            f"[data_entry_operations] operation='{operation}', sheet='{sheet_name}', skip_header={skip_header}, has_headers={has_headers}"
        )
        try:
            result = data_entry_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                data=data,
                rows=rows,
                headers=headers,
                row_id=row_id,
                column_name=column_name,
                new_data=new_data,
                skip_header=skip_header,
                has_headers=has_headers
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[data_entry_operations] Error: {e}", exc_info=True)
            raise


    def data_retrieval_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        cell: Optional[str] = None,
        row_id: Optional[str] = None,
        column_name: Optional[str] = None,
        condition_type: Optional[str] = None,
        condition_value: Optional[str] = None,
        start_row: int = 1,
        max_rows: int = 20,
        include_headers: bool = False,
        skip_header: bool = True,
        has_headers: bool = True
    ) -> Dict[str, Any]:
        """
        Extends data retrieval operations (retrieve_cell, filter_rows, etc.).
        """
        self.logger.info(
            f"[data_retrieval_operations] operation='{operation}', sheet='{sheet_name}', start_row={start_row}, skip_header={skip_header}, has_headers={has_headers}"
        )
        try:
            if operation == "filter_rows":
                result = data_retrieval_operations(
                    operation=operation,
                    path=path,
                    file_name=file_name,
                    sheet_name=sheet_name,
                    column_name=column_name,
                    condition_type=condition_type,
                    condition_value=condition_value,
                    skip_header=skip_header,
                    has_headers=has_headers
                )
            else:
                result = data_retrieval_operations(
                    operation=operation,
                    path=path,
                    file_name=file_name,
                    sheet_name=sheet_name,
                    cell=cell,
                    row_id=row_id,
                    column_name=column_name,
                    condition_type=condition_type,
                    condition_value=condition_value,
                    start_row=start_row,
                    max_rows=max_rows,
                    include_headers=include_headers,
                    has_headers=has_headers
                )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[data_retrieval_operations] Error: {e}", exc_info=True)
            raise


    def data_analysis_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        required_sheets: Optional[List[str]] = None,
        required_headers: Optional[Dict[str, List[str]]] = None,
        sheet_name: Optional[str] = None,
        pivot_table_config: Optional[Dict[str, Any]] = None,
        files_list: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Extends data analysis operations (pivot tables, etc.).
        """
        self.logger.info(f"[data_analysis_operations] operation='{operation}', file='{file_name}'")
        try:
            result = data_analysis_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                required_sheets=required_sheets,
                required_headers=required_headers,
                sheet_name=sheet_name,
                pivot_table_config=pivot_table_config,
                files_list=files_list,
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[data_analysis_operations] Error: {e}", exc_info=True)
            raise


    def formula_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        cell: Optional[str] = None,
        formula: Optional[str] = None,
        column_name: Optional[str] = None,
        formula_template: Optional[str] = None,
        start_row: int = 1,
        range_name: Optional[str] = None,
        cell_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extends formula operations dispatcher.
        """
        self.logger.info(f"[formula_operations] operation='{operation}', cell='{cell}'")
        try:
            result = formula_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                cell=cell,
                formula=formula,
                column_name=column_name,
                formula_template=formula_template,
                start_row=start_row,
                range_name=range_name,
                cell_range=cell_range,
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[formula_operations] Error: {e}", exc_info=True)
            raise


    def formatting_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        cell: Optional[str] = None,
        style_rules: Optional[Dict[str, Any]] = None,
        formatting_rules: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extends formatting operations dispatcher.
        """
        self.logger.info(f"[formatting_operations] operation='{operation}', sheet='{sheet_name}'")
        try:
            result = formatting_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                cell=cell,
                style_rules=style_rules,
                formatting_rules=formatting_rules,
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[formatting_operations] Error: {e}", exc_info=True)
            raise


    def data_validation_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        range_to_remove: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extends data validation operations dispatcher.
        """
        self.logger.info(f"[data_validation_operations] operation='{operation}', sheet='{sheet_name}'")
        try:
            result = data_validation_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                validation_rules=validation_rules,
                range_to_remove=range_to_remove,
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[data_validation_operations] Error: {e}", exc_info=True)
            raise


    def data_transformation_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        source_range: Optional[str] = None,
        destination_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extends data transformation operations dispatcher.
        """
        self.logger.info(f"[data_transformation_operations] operation='{operation}', sheet='{sheet_name}'")
        try:
            result = data_transformation_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                source_range=source_range,
                destination_range=destination_range,
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[data_transformation_operations] Error: {e}", exc_info=True)
            raise


    def chart_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/spreadsheets",
        file_name: str = "example_spreadsheet.xlsx",
        sheet_name: Optional[str] = None,
        chart_type: Optional[str] = None,
        data_range: Optional[str] = None,
        categories_range: Optional[str] = None,
        destination_cell: str = "A10",
        title: Optional[str] = None,
        x_title: Optional[str] = None,
        y_title: Optional[str] = None,
        legend_position: str = "r",
        style: int = 2,
        show_data_labels: bool = False,
        overlap: Optional[int] = None,
        grouping: Optional[str] = None,
        series_names: Optional[List[str]] = None,
        chart_title: Optional[str] = None,
        new_data_range: Optional[str] = None,
        new_categories_range: Optional[str] = None,
        new_title: Optional[str] = None,
        new_x_title: Optional[str] = None,
        new_y_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extends chart operations dispatcher.
        """
        self.logger.info(
            f"[chart_operations] operation='{operation}', sheet='{sheet_name}', chart_type='{chart_type}', destination='{destination_cell}'"
        )
        try:
            from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.spreadsheet_entrypoint import chart_operations
            result = chart_operations(
                operation=operation,
                path=path,
                file_name=file_name,
                sheet_name=sheet_name,
                chart_type=chart_type,
                data_range=data_range,
                categories_range=categories_range,
                destination_cell=destination_cell,
                title=title,
                x_title=x_title,
                y_title=y_title,
                legend_position=legend_position,
                style=style,
                show_data_labels=show_data_labels,
                overlap=overlap,
                grouping=grouping,
                series_names=series_names,
                chart_title=chart_title,
                new_data_range=new_data_range,
                new_categories_range=new_categories_range,
                new_title=new_title,
                new_x_title=new_x_title,
                new_y_title=new_y_title
            )
            return prepare_tool_output(result)
        except Exception as e:
            self.logger.error(f"[chart_operations] Error: {e}", exc_info=True)
            raise


    def identify_subscriber(
        self,
        contract_holder_name: str = None,
        phone_number: str = None,
        contract_holder_address: str = None,
        date_of_birth: str = None,
        email_address: str = None,
        personal_id_number: str = None,
        id_card_series: str = None,
        client_code: str = None
    ) -> dict:
        """
        Identifies a subscriber in the PrettyMobile system based on provided details.

        Args:
            contract_holder_name: Subscriber's name.
            phone_number: Subscriber's phone.
            contract_holder_address: Address.
            date_of_birth: 'yyyy-mm-dd'.
            email_address: Email.
            personal_id_number: Personal ID (CNP).
            id_card_series: ID card series.
            client_code: Client code.

        Returns:
            dict: status, message, and result (list of matching records or None).
        """
        self.logger.info("[identify_subscriber] Starting identification.")
        try:
            provided_details = {
                "contract_holder_name": contract_holder_name,
                "phone_number": phone_number,
                "contract_holder_address": contract_holder_address,
                "date_of_birth": date_of_birth,
                "email_address": email_address,
                "personal_id_number": personal_id_number,
                "id_card_series": id_card_series,
                "client_code": client_code
            }
            # Clean inputs
            cleaned = {}
            for k, v in provided_details.items():
                if v:
                    cleaned[k] = v.strip().lower() if k != "date_of_birth" else v.strip()
            if len(cleaned) < 3:
                msg = "At least three details are required for identification."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}

            # Read CSV
            csv_path = os.path.join(os.path.dirname(__file__), "data", "csv", "identify_subscriber.csv")
            resp = self.csv_helpers.handle_csv(csv_path, "read")
            if not resp["status"]:
                return {"status": False, "message": resp["message"], "result": None}
            df = resp["result"]

            # Validate headers
            expected = [
                "contract_holder_name", "phone_number", "contract_holder_address",
                "date_of_birth", "email_address", "personal_id_number",
                "id_card_series", "client_code"
            ]
            if list(df.columns) != expected:
                msg = f"CSV headers mismatch. Expected {expected}, got {list(df.columns)}"
                self.logger.error(msg)
                return {"status": False, "message": msg, "result": None}

            # Clean and match
            df_clean = self.csv_helpers.clean_dataframe(
                df,
                columns_to_lower=[c for c in expected if c != "date_of_birth"],
                columns_to_strip=expected
            )
            matches = self.csv_helpers.find_matching_records(df_clean, search_criteria=cleaned, min_matches=len(cleaned))
            if matches:
                return {"status": True, "message": "Subscriber(s) identified.", "result": matches}
            else:
                msg = "No subscriber matched."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}
        except Exception as e:
            msg = f"[identify_subscriber] Error: {e}"
            self.logger.error(msg, exc_info=True)
            return {"status": False, "message": msg, "result": None}


    def retrieve_billing_details(self, contract_holder_name: str) -> dict:
        """
        Retrieves billing details for a subscriber by name.

        Args:
            contract_holder_name: Contract holder's name.

        Returns:
            dict: status, message, and result (list of invoices).
        """
        self.logger.info("[retrieve_billing_details] Fetching billing for '%s'.", contract_holder_name)
        try:
            if not contract_holder_name or not contract_holder_name.strip():
                msg = "Contract holder's name is required."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}

            cleaned = contract_holder_name.strip().lower()
            csv_path = os.path.join(os.path.dirname(__file__), "data", "csv", "retrieve_billing_details.csv")
            resp = self.csv_helpers.handle_csv(csv_path, "read")
            if not resp["status"]:
                return {"status": False, "message": resp["message"], "result": None}
            df = resp["result"]

            expected = ["contract_holder_name", "invoice_number", "issue_date", "amount_due", "payment_status"]
            if list(df.columns) != expected:
                msg = f"CSV headers mismatch. Expected {expected}, got {list(df.columns)}"
                self.logger.error(msg)
                return {"status": False, "message": msg, "result": None}

            df["contract_holder_name_cleaned"] = df["contract_holder_name"].fillna("").astype(str).str.strip().str.lower()
            matched = df[df["contract_holder_name_cleaned"] == cleaned]
            if not matched.empty:
                result = matched.drop(columns=["contract_holder_name_cleaned"]).to_dict(orient="records")
                return {"status": True, "message": "Billing details retrieved.", "result": result}
            else:
                msg = "No billing records found."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}
        except Exception as e:
            msg = f"[retrieve_billing_details] Error: {e}"
            self.logger.error(msg, exc_info=True)
            return {"status": False, "message": msg, "result": None}


    def manage_services(
        self,
        contract_holder_name: str,
        action: str,
        service_type: Optional[str] = None,
        service_status: Optional[str] = None,
        current_package: Optional[str] = None,
        new_package: Optional[str] = None,
        available_options: Optional[str] = None,
        current_service_type: Optional[str] = None
    ) -> dict:
        """
        Manages subscriber services based on provided details and requested action.

        Args:
            contract_holder_name: Name of the contract holder.
            action: One of 'check_services', 'activate_deactivate_service',
                    'modify_package', 'modify_services'.
            service_type: e.g. 'Internet'.
            service_status: 'Active' or 'Inactive'.
            current_package: Current package name.
            new_package: New package name.
            available_options: Options string.
            current_service_type: Existing service type when modifying.

        Returns:
            dict: status, message, and result.
        """
        self.logger.info("[manage_services] action='%s' for '%s'.", action, contract_holder_name)
        try:
            if not contract_holder_name.strip():
                msg = "Contract holder's name is required."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}
            if not action:
                msg = "Action is required."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}

            cleaned = {
                "contract_holder_name": contract_holder_name.strip().lower(),
                "action": action.lower(),
                "service_type": service_type.strip().lower() if service_type else None,
                "service_status": service_status.strip().lower() if service_status else None,
                "current_package": current_package.strip().lower() if current_package else None,
                "new_package": new_package.strip().lower() if new_package else None,
                "available_options": available_options.strip() if available_options else None,
                "current_service_type": current_service_type.strip().lower() if current_service_type else None
            }

            csv_path = os.path.join(os.path.dirname(__file__), "data", "csv", "manage_services.csv")
            resp = self.csv_helpers.handle_csv(csv_path, "read")
            if not resp["status"]:
                return {"status": False, "message": resp["message"], "result": None}
            df_orig = resp["result"]

            expected = ["contract_holder_name", "service_type", "service_status", "current_package", "available_options"]
            if list(df_orig.columns) != expected:
                msg = f"CSV headers mismatch. Expected {expected}, got {list(df_orig.columns)}"
                self.logger.error(msg)
                return {"status": False, "message": msg, "result": None}

            df_clean = self.csv_helpers.clean_dataframe(
                df_orig.copy(),
                columns_to_lower=["contract_holder_name", "service_type", "service_status", "current_package"],
                columns_to_strip=["contract_holder_name", "service_type", "service_status", "current_package"]
            )

            # Find matching records
            matches_clean = self.csv_helpers.find_matching_records(
                df_clean,
                search_criteria={"contract_holder_name": cleaned["contract_holder_name"]},
                min_matches=1
            )
            if not matches_clean:
                msg = "No subscriber found."
                self.logger.warning(msg)
                return {"status": False, "message": msg, "result": None}

            # Map back to original
            matched_original = []
            for rec in matches_clean:
                mask = (
                    (df_orig["contract_holder_name"].str.lower() == rec["contract_holder_name"]) &
                    (df_orig["service_type"].str.lower() == rec["service_type"]) &
                    (df_orig["service_status"].str.lower() == rec["service_status"]) &
                    (df_orig["current_package"].str.lower() == rec["current_package"]) &
                    (df_orig["available_options"].str.lower() == rec["available_options"].lower())
                )
                rows = df_orig[mask]
                if not rows.empty:
                    matched_original.append(rows.iloc[0].to_dict())

            act = cleaned["action"]
            # 1. check_services
            if act == "check_services":
                return {"status": True, "message": "Current services retrieved.", "result": matched_original}

            # 2. activate_deactivate_service
            if act == "activate_deactivate_service":
                if not cleaned["service_type"] or not cleaned["service_status"]:
                    msg = "Service type and status required."
                    self.logger.warning(msg)
                    return {"status": False, "message": msg, "result": None}
                if cleaned["service_status"] not in ("active", "inactive"):
                    msg = "Status must be 'Active' or 'Inactive'."
                    self.logger.warning(msg)
                    return {"status": False, "message": msg, "result": None}
                updates = {"service_status": cleaned["service_status"].capitalize()}
                cond = lambda r: (
                    r["contract_holder_name"].strip().lower() == cleaned["contract_holder_name"] and
                    r["service_type"].strip().lower() == cleaned["service_type"]
                )
                upd = self.csv_helpers.handle_csv(csv_path, "update", updates=updates, condition=cond)
                if upd["status"]:
                    verb = "activated" if cleaned["service_status"] == "active" else "deactivated"
                    msg = f"Service '{service_type}' {verb} successfully."
                    return {"status": True, "message": msg, "result": None}
                else:
                    return {"status": False, "message": upd["message"], "result": None}

            # 3. modify_package
            if act == "modify_package":
                if not (cleaned["service_type"] and cleaned["current_package"] and cleaned["new_package"]):
                    msg = "service_type, current_package and new_package required."
                    self.logger.warning(msg)
                    return {"status": False, "message": msg, "result": None}
                valid = ["pretty250", "pretty500", "pretty1000"]
                if cleaned["new_package"] not in valid:
                    msg = f"New package must be {', '.join(valid)}."
                    self.logger.warning(msg)
                    return {"status": False, "message": msg, "result": None}
                updates = {"current_package": new_package}
                cond = lambda r: (
                    r["contract_holder_name"].strip().lower() == cleaned["contract_holder_name"] and
                    r["service_type"].strip().lower() == cleaned["service_type"] and
                    r["current_package"].strip().lower() == cleaned["current_package"]
                )
                upd = self.csv_helpers.handle_csv(csv_path, "update", updates=updates, condition=cond)
                if upd["status"]:
                    msg = f"Package for '{service_type}' changed from '{current_package}' to '{new_package}'."
                    return {"status": True, "message": msg, "result": None}
                else:
                    return {"status": False, "message": upd["message"], "result": None}

            # 4. modify_services
            if act == "modify_services":
                if not (cleaned["service_type"] or cleaned["available_options"]):
                    msg = "service_type or available_options required."
                    self.logger.warning(msg)
                    return {"status": False, "message": msg, "result": None}
                updates: Dict[str, Any] = {}
                if cleaned["service_type"]:
                    updates["service_type"] = service_type
                if cleaned["available_options"]:
                    updates["available_options"] = available_options
                if cleaned["service_type"] and cleaned["current_service_type"]:
                    cond = lambda r: (
                        r["contract_holder_name"].strip().lower() == cleaned["contract_holder_name"] and
                        r["service_type"].strip().lower() == cleaned["current_service_type"]
                    )
                else:
                    cond = lambda r: (
                        r["contract_holder_name"].strip().lower() == cleaned["contract_holder_name"]
                    )
                upd = self.csv_helpers.handle_csv(csv_path, "update", updates=updates, condition=cond)
                if upd["status"]:
                    parts = []
                    if "service_type" in updates:
                        parts.append(f"service type changed to '{service_type}'")
                    if "available_options" in updates:
                        parts.append("available options updated")
                    msg = ". ".join(parts).capitalize() + "."
                    return {"status": True, "message": msg, "result": None}
                else:
                    return {"status": False, "message": upd["message"], "result": None}

            # unsupported
            msg = f"Unsupported action: {action}"
            self.logger.warning(msg)
            return {"status": False, "message": msg, "result": None}

        except Exception as e:
            msg = f"[manage_services] Error: {e}"
            self.logger.error(msg, exc_info=True)
            return {"status": False, "message": msg, "result": None}


    def csv_operations(
        self,
        operation: str,
        path: str = "flexiai/toolsmith/data/csv",
        file_name: str = "",
        index: Optional[int] = None,
        column: Optional[Union[str,int]] = None,
        row: Optional[Dict[str,Any]] = None,
        rows: Optional[List[Dict[str,Any]]] = None,
        value: Optional[Any] = None,
        condition_type: Optional[str] = None,
        condition_value: Optional[Any] = None,
        headers: Optional[List[str]] = None,
        required_columns: Optional[List[str]] = None,
    ) -> Dict[str,Any]:
        """
        Generic CSV dispatcher. Agent supplies "operation" plus only the kwargs needed.
        """
        self.logger.info(f"[csv_operations] operation={operation!r} file_name={file_name!r}")
        try:
            resp = csv_entrypoint(
                operation=operation,
                path=path,
                file_name=file_name,
                index=index,
                column=column,
                row=row,
                rows=rows,
                value=value,
                condition_type=condition_type,
                condition_value=condition_value,
                headers=headers,
                required_columns=required_columns,
            )

            # Log any explicit CSV‐level failure
            if not resp.get("status", False):
                self.logger.error(f"[csv_operations][{operation}] failed: {resp.get('message')}")

            return prepare_tool_output(resp)

        except Exception:
            # Wrap unexpected exceptions in our standard error shape
            self.logger.exception(f"[csv_operations][{operation}] unexpected crash")
            err = {"status": False, "message": f"Unexpected error in csv_operations '{operation}'", "result": None}
            return prepare_tool_output(err)

