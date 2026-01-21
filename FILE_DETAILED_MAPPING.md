# FlexiAI Toolsmith - Detailed File-by-File Mapping

This document provides detailed information about each file, including exact imports, exports, and relationships.

---

## Root Level Files

### `app.py`
**Purpose:** Web application entry point (Quart server)

**Imports:**
- `logging`, `uuid`, `os`, `csv` (stdlib)
- `quart` (Quart, render_template, request, g, session, Response, redirect, url_for, jsonify)
- `flexiai.config.models.GeneralSettings`
- `flexiai.config.logging_config.setup_logging`
- `flexiai.controllers.quart_chat_controller` (as qcc)

**Exports:**
- `app` (Quart instance)

**Relationships:**
- Uses: `GeneralSettings`, `setup_logging`, `quart_chat_controller`
- Used by: Hypercorn server, Docker

**Key Functions:**
- `initialize_controller()` - Sets up QuartChatController
- `load_user()` - Manages user session
- `home()` - Landing page
- `submit_user_info()` - Form submission handler

---

### `chat.py`
**Purpose:** CLI application entry point

**Imports:**
- `logging`, `asyncio` (stdlib)
- `flexiai.config.models.GeneralSettings`
- `flexiai.config.logging_config.setup_logging`
- `flexiai.controllers.cli_chat_controller.CLIChatController`

**Exports:**
- `main()` async function

**Relationships:**
- Uses: `GeneralSettings`, `setup_logging`, `CLIChatController`
- Used by: Direct execution (`python chat.py`)

---

## Configuration Module

### `flexiai/config/models.py`
**Purpose:** Pydantic settings models for all environment variables

**Imports:**
- `typing.Optional`
- `pydantic_settings.BaseSettings, SettingsConfigDict`
- `pydantic.Field`

**Exports:**
- `OpenAISettings` class
- `AzureOpenAISettings` class
- `DeepSeekSettings` class
- `QwenSettings` class
- `GitHubAzureInferenceSettings` class
- `GeneralSettings` class

**Relationships:**
- Used by: `client_settings.py`, `channel_manager.py`, `controllers`

**Key Classes:**
- Each Settings class defines environment variables for a provider
- All use `.env` file via `SettingsConfigDict(env_file=".env")`

---

### `flexiai/config/client_settings.py`
**Purpose:** Validates and loads provider-specific settings

**Imports:**
- `logging`
- `pydantic.ValidationError`
- `flexiai.config.models.*` (all Settings classes)

**Exports:**
- `config` dict (validated settings)

**Relationships:**
- Uses: `models.*Settings`
- Used by: `credentials.py`

**Key Functions:**
- Validates settings based on `CREDENTIAL_TYPE`
- Raises errors if required settings are missing

---

### `flexiai/config/client_factory.py`
**Purpose:** Factory for creating singleton AI client

**Imports:**
- `logging`, `asyncio` (stdlib)
- `typing.Any`
- `flexiai.credentials.credentials.get_client` (as get_unified_client)

**Exports:**
- `get_client()` - Synchronous client getter
- `get_client_async()` - Asynchronous client getter

**Relationships:**
- Uses: `credentials.get_client`
- Used by: All controllers (`cli_chat_controller`, `quart_chat_controller`)

**Key Functions:**
- `get_client()` - Returns cached client or creates new one
- `get_client_async()` - Wraps get_client in executor for async contexts

---

### `flexiai/config/logging_config.py`
**Purpose:** Configures application-wide logging

**Imports:**
- `os`, `logging` (stdlib)
- `logging.handlers.RotatingFileHandler`

**Exports:**
- `setup_logging()` function

**Relationships:**
- Used by: `app.py`, `chat.py`

**Key Functions:**
- `setup_logging()` - Configures file and console logging with rotation

---

## Credentials Module

### `flexiai/credentials/credentials.py`
**Purpose:** Unified credential manager for all AI providers

**Imports:**
- `logging`, `asyncio` (stdlib)
- `abc.ABC, abstractmethod`
- `typing.Any`
- `flexiai.config.client_settings.config`
- `openai` (OpenAI client)

**Exports:**
- `get_client()` - Returns configured OpenAI-compatible client

**Relationships:**
- Uses: `client_settings.config`
- Used by: `client_factory.py`

**Key Functions:**
- Creates OpenAI client with provider-specific configuration
- Supports: OpenAI, Azure, DeepSeek, Qwen, GitHub Azure Inference

---

## Controllers Module

### `flexiai/controllers/cli_chat_controller.py`
**Purpose:** Manages CLI chat loop

**Imports:**
- `logging`, `asyncio` (stdlib)
- `logging.LoggerAdapter`
- `typing.Any`
- `flexiai.config.client_factory.get_client_async`
- `flexiai.core.handlers.run_thread_manager.RunThreadManager`
- `flexiai.toolsmith.tools_manager.ToolsManager`
- `flexiai.core.handlers.handler_factory.create_event_handler`
- `flexiai.core.events.event_bus.global_event_bus`
- `flexiai.channels.channel_manager.get_active_channels`
- `flexiai.channels.multi_channel_publisher.MultiChannelPublisher`

**Exports:**
- `CLIChatController` class

**Relationships:**
- Uses: All core handlers, tools_manager, channels, event_bus
- Used by: `chat.py`

**Key Methods:**
- `create_async()` - Factory method
- `run_chat_loop()` - Main chat loop
- `process_user_message()` - Handles user input

---

### `flexiai/controllers/quart_chat_controller.py`
**Purpose:** Manages web chat via HTTP/SSE

**Imports:**
- `asyncio`, `json`, `threading`, `logging` (stdlib)
- `typing.Optional`
- `quart` (Blueprint, request, jsonify, render_template, Response, g)
- `flexiai.config.models.GeneralSettings`
- `flexiai.config.client_factory.get_client_async`
- `flexiai.core.handlers.run_thread_manager.RunThreadManager`
- `flexiai.toolsmith.tools_manager.ToolsManager`
- `flexiai.core.events.event_bus.global_event_bus`
- `flexiai.core.events.sse_manager.SSEManager`
- `flexiai.core.handlers.handler_factory.create_event_handler`

**Exports:**
- `QuartChatController` class
- `chat_bp` Blueprint
- `controller_instance` (singleton)

**Relationships:**
- Uses: All core handlers, tools_manager, sse_manager, event_bus
- Used by: `app.py`

**Key Methods:**
- `create_async()` - Factory method
- `process_user_message()` - Handles HTTP POST
- `stream_events()` - SSE endpoint
- `render_chat_page()` - Chat UI route

---

## Core Handlers Module

### `flexiai/core/handlers/run_thread_manager.py`
**Purpose:** Manages OpenAI Assistant API threads, runs, and messages

**Imports:**
- `logging`, `asyncio` (stdlib)
- `typing.Any, Optional`
- OpenAI client

**Exports:**
- `RunThreadManager` class

**Relationships:**
- Uses: OpenAI client
- Used by: All controllers, event_handler, tools_manager

**Key Methods:**
- `create_thread()` - Creates new thread
- `create_message()` - Adds message to thread
- `create_run()` - Starts assistant run
- `get_run_status()` - Checks run status
- `get_messages()` - Retrieves messages
- `submit_tool_outputs()` - Submits tool results

---

### `flexiai/core/handlers/event_handler.py`
**Purpose:** Processes streaming events from AI service

**Imports:**
- `json`, `logging`, `asyncio` (stdlib)
- `typing.Any, Optional, Dict, Callable`
- `flexiai.core.handlers.tool_call_executor.ToolCallExecutor`
- `flexiai.core.handlers.run_thread_manager.RunThreadManager`
- `flexiai.core.handlers.event_dispatcher.EventDispatcher`
- `flexiai.core.events.event_models.MessageDeltaEvent`
- `flexiai.channels.multi_channel_publisher.MultiChannelPublisher`
- `flexiai.core.events.rolling_event_buffer.RollingEventBuffer`
- `flexiai.core.events.session.ChatSession`
- `flexiai.controllers.quart_chat_controller.QuartChatController` (for type hints)

**Exports:**
- `EventHandler` class

**Relationships:**
- Uses: tool_call_executor, run_thread_manager, event_dispatcher, channels, events, rolling_event_buffer, session
- Used by: Controllers (via handler_factory)
- Note: Imports QuartChatController for type hints only (circular dependency handled via TYPE_CHECKING)

**Key Methods:**
- `handle_streaming_events()` - Main event processing loop
- `_handle_message_delta()` - Processes message deltas
- `_handle_tool_call()` - Handles tool calls
- `_handle_run_complete()` - Handles run completion

---

### `flexiai/core/handlers/event_dispatcher.py`
**Purpose:** Routes events to appropriate handlers

**Imports:**
- `logging`
- `typing.Any, Dict, Callable`
- `flexiai.core.events.event_models.*`

**Exports:**
- `EventDispatcher` class

**Relationships:**
- Uses: event_models
- Used by: event_handler

**Key Methods:**
- `dispatch()` - Routes event to handler
- `register_handler()` - Registers event handler
- Maps event types to handler functions

---

### `flexiai/core/handlers/handler_factory.py`
**Purpose:** Creates EventHandler instances

**Imports:**
- `typing.Any, Dict, Callable, Optional`
- `flexiai.core.handlers.event_handler.EventHandler`
- `flexiai.core.handlers.run_thread_manager.RunThreadManager`
- `flexiai.core.handlers.event_dispatcher.EventDispatcher`

**Exports:**
- `create_event_handler()` function

**Relationships:**
- Uses: event_handler, run_thread_manager, event_dispatcher
- Used by: Controllers

**Key Functions:**
- `create_event_handler()` - Factory function that wires all dependencies

---

### `flexiai/core/handlers/tool_call_executor.py`
**Purpose:** Executes tool calls from AI assistant

**Imports:**
- `json`, `logging` (stdlib)
- `typing.Any, Dict, Callable`
- `flexiai.toolsmith.tools_registry.ToolsRegistry`
- `flexiai.utils.context_utils.return_context`

**Exports:**
- `ToolCallExecutor` class

**Relationships:**
- Uses: tools_registry, context_utils
- Used by: event_handler

**Key Methods:**
- `execute()` - Executes a tool call
- `_execute_tool()` - Internal tool execution
- Uses `return_context()` to truncate tool outputs to fit token limits

---

## Core Events Module

### `flexiai/core/events/event_models.py`
**Purpose:** Pydantic models for all event types

**Imports:**
- `pydantic.BaseModel, Field`
- `typing.Any, Dict, List`
- `time` (stdlib)

**Exports:**
- Event model classes (MessageDeltaEvent, ThreadRunEvent, etc.)

**Relationships:**
- Used by: All event-related modules

**Key Classes:**
- `MessageDeltaEvent` - Message delta updates
- `ThreadRunEvent` - Thread run status
- `ToolCallEvent` - Tool call requests
- Other event types

---

### `flexiai/core/events/event_bus.py`
**Purpose:** Pub/sub system for events (singleton)

**Imports:**
- `logging`
- `typing.Any, Callable, Dict, List`

**Exports:**
- `global_event_bus` instance
- `EventBus` class

**Relationships:**
- Used by: Controllers, event_handler, channels

**Key Methods:**
- `subscribe()` - Subscribe to event type
- `publish()` - Publish event
- `unsubscribe()` - Unsubscribe from event type

---

### `flexiai/core/events/sse_manager.py`
**Purpose:** Manages Server-Sent Events for web clients

**Imports:**
- `collections.defaultdict, deque`
- `threading`
- `logging`

**Exports:**
- `SSEManager` class
- `global_sse_manager` instance

**Relationships:**
- Used by: quart_channel, quart_chat_controller

**Key Methods:**
- `register_client()` - Register SSE client
- `send_event()` - Send event to client
- `unregister_client()` - Remove client

---

### `flexiai/core/events/session.py`
**Purpose:** Manages chat session state

**Imports:**
- `threading`, `asyncio` (stdlib)
- `flexiai.core.events.rolling_event_buffer.RollingEventBuffer`

**Exports:**
- `ChatSession` class

**Relationships:**
- Uses: rolling_event_buffer
- Used by: event_handler

**Key Methods:**
- Manages session state and event history

---

### `flexiai/core/events/rolling_event_buffer.py`
**Purpose:** Maintains rolling buffer of recent events

**Imports:**
- `logging`
- `collections.OrderedDict`
- `typing.Dict, List`

**Exports:**
- `RollingEventBuffer` class

**Relationships:**
- Used by: session

**Key Methods:**
- `add()` - Add event to buffer
- `get_recent()` - Get recent events
- Maintains fixed-size buffer

---

## Channels Module

### `flexiai/channels/base_channel.py`
**Purpose:** Abstract base class for all channels

**Imports:**
- `abc.ABC, abstractmethod`
- `typing.Any`

**Exports:**
- `BaseChannel` abstract class

**Relationships:**
- Base for: cli_channel, quart_channel, redis_channel

**Key Methods:**
- `publish_event()` - Abstract method to be implemented

---

### `flexiai/channels/cli_channel.py`
**Purpose:** Publishes events to console

**Imports:**
- `logging`
- `typing.Any`
- `flexiai.channels.base_channel.BaseChannel`

**Exports:**
- `CLIChannel` class

**Relationships:**
- Uses: base_channel
- Used by: channel_manager, multi_channel_publisher

**Key Methods:**
- `publish_event()` - Prints events to stdout

---

### `flexiai/channels/quart_channel.py`
**Purpose:** Publishes events via SSE to web clients

**Imports:**
- `logging`, `json` (stdlib)
- `typing.Any`
- `pydantic.BaseModel`
- `quart` (g, has_request_context)
- `flexiai.channels.base_channel.BaseChannel`
- `flexiai.core.events.sse_manager.global_sse_manager`

**Exports:**
- `QuartChannel` class

**Relationships:**
- Uses: base_channel, sse_manager
- Used by: channel_manager, multi_channel_publisher

**Key Methods:**
- `publish_event()` - Sends events via SSE

---

### `flexiai/channels/redis_channel.py`
**Purpose:** Publishes events to Redis Pub/Sub

**Imports:**
- `logging`, `json` (stdlib)
- `typing.Any`
- `redis`
- `flexiai.channels.base_channel.BaseChannel`

**Exports:**
- `RedisChannel` class

**Relationships:**
- Uses: base_channel, redis
- Used by: channel_manager, multi_channel_publisher

**Key Methods:**
- `publish_event()` - Publishes to Redis channel

---

### `flexiai/channels/channel_manager.py`
**Purpose:** Factory for creating active channels

**Imports:**
- `logging`
- `flexiai.config.models.GeneralSettings`
- `flexiai.channels.cli_channel.CLIChannel`
- `flexiai.channels.redis_channel.RedisChannel`
- `flexiai.channels.quart_channel.QuartChannel`

**Exports:**
- `get_active_channels()` function

**Relationships:**
- Uses: GeneralSettings, all channel classes
- Used by: multi_channel_publisher, controllers

**Key Functions:**
- `get_active_channels()` - Returns list of active channels based on ACTIVE_CHANNELS config

---

### `flexiai/channels/multi_channel_publisher.py`
**Purpose:** Publishes to multiple channels simultaneously

**Imports:**
- `logging`
- `typing.Any`
- `flexiai.channels.channel_manager.get_active_channels`

**Exports:**
- `MultiChannelPublisher` class

**Relationships:**
- Uses: channel_manager
- Used by: event_handler

**Key Methods:**
- `publish()` - Publishes to all active channels

---

## Toolsmith Module

### `flexiai/toolsmith/tools_manager.py`
**Purpose:** Core tool implementations

**Imports:**
- `logging`, `threading`, `subprocess`, `os`, `urllib`, `json` (stdlib)
- `typing.Any, Dict, Tuple, List, Optional, Union, TYPE_CHECKING`
- `dotenv.load_dotenv`
- `googleapiclient.discovery.build`
- `googleapiclient.errors.HttpError`
- `flexiai.core.handlers.run_thread_manager.RunThreadManager`
- `flexiai.toolsmith.tools_infrastructure.csv_helpers.CSVHelpers`
- `flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.*`
- `flexiai.toolsmith.tools_infrastructure.csv_infrastructure.csv_entrypoint.csv_entrypoint`
- `flexiai.toolsmith.tools_infrastructure.security_audit.SecurityAudit`

**Exports:**
- `ToolsManager` class

**Relationships:**
- Uses: run_thread_manager, all infrastructure modules
- Used by: tools_registry, controllers

**Key Methods:**
- `save_processed_content()` - RAG storage
- `load_processed_content()` - RAG retrieval
- `initialize_agent()` - Agent coordination
- `communicate_with_assistant()` - Inter-agent communication
- `search_youtube()` - YouTube search
- `search_on_youtube()` - YouTube search with embeds
- `csv_operations()` - CSV operations dispatcher
- `file_operations()` - Spreadsheet file operations
- `security_audit()` - Security auditing
- Many more tool methods...

---

### `flexiai/toolsmith/tools_registry.py`
**Purpose:** Maps tool names to callable functions

**Imports:**
- `logging`
- `typing.Any, Callable, Dict`
- `flexiai.toolsmith.tools_manager.ToolsManager`

**Exports:**
- `ToolsRegistry` class
- `RegistryError` exception

**Relationships:**
- Uses: tools_manager
- Used by: tool_call_executor

**Key Methods:**
- `map_core_tools()` - Registers core tools
- `map_custom_tools()` - Registers custom tools
- `get_tool()` - Retrieves tool by name
- `get_all_tools()` - Returns all registered tools

---

## CSV Infrastructure

### `flexiai/toolsmith/tools_infrastructure/csv_infrastructure/csv_entrypoint.py`
**Purpose:** Main CSV operations dispatcher

**Imports:**
- All CSV operation modules
- All CSV utils
- CSV exceptions

**Exports:**
- `csv_entrypoint()` function

**Relationships:**
- Uses: All CSV operations, utils, exceptions
- Used by: tools_manager

**Key Functions:**
- `csv_entrypoint()` - Routes CSV operations to appropriate handlers

---

### CSV Operations Files
All follow similar pattern:
- Import: `csv_manager`, `utils`, `exceptions`
- Export: Operation-specific functions
- Used by: `csv_entrypoint`

**Files:**
- `operations/create_operations.py` - Create CSV files
- `operations/read_operations.py` - Read CSV data
- `operations/update_operations.py` - Update CSV rows
- `operations/delete_operations.py` - Delete CSV rows/files
- `operations/filter_operations.py` - Filter CSV rows
- `operations/data_validation_operations.py` - Validate data
- `operations/data_transformation_operations.py` - Transform data

---

### CSV Utilities
- `utils/file_handler.py` - File path validation
- `utils/error_handler.py` - Error response formatting
- `utils/mixed_helpers.py` - Type conversion

---

### CSV Managers & Exceptions
- `managers/csv_manager.py` - Core CSV operations using pandas
- `exceptions/csv_exceptions.py` - CSV-specific exceptions

---

## Spreadsheet Infrastructure

Similar structure to CSV infrastructure:

### `flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/spreadsheet_entrypoint.py`
**Purpose:** Main spreadsheet operations dispatcher

**Imports:**
- All spreadsheet operation modules
- All spreadsheet utils
- Spreadsheet exceptions

**Exports:**
- Multiple operation functions (file_operations, sheet_operations, etc.)

**Relationships:**
- Uses: All spreadsheet operations, utils, exceptions
- Used by: tools_manager

---

### Spreadsheet Operations Files
Similar to CSV operations:
- `operations/file_operations.py` - Create/open/close spreadsheets
- `operations/sheet_operations.py` - Sheet management
- `operations/data_entry_operations.py` - Write data
- `operations/data_retrieval_operations.py` - Read data
- `operations/data_analysis_operations.py` - Analyze data
- `operations/formula_operations.py` - Formulas
- `operations/formatting_operations.py` - Formatting
- `operations/data_validation_operations.py` - Validation
- `operations/data_transformation_operations.py` - Transformation
- `operations/chart_operations.py` - Charts

---

## Database Module

### `flexiai/database/connection.py`
**Purpose:** Database connection setup

**Imports:**
- `os` (stdlib)
- `sqlalchemy` (create_engine, sessionmaker, declarative_base)

**Exports:**
- `engine` - SQLAlchemy engine
- `SessionLocal` - Session factory
- `Base` - Declarative base

**Relationships:**
- Used by: models

---

### `flexiai/database/models.py`
**Purpose:** Database ORM models

**Imports:**
- `datetime` (stdlib)
- `sqlalchemy` (Column, Integer, String, DateTime, Text, ForeignKey, relationship)
- `flexiai.database.connection.Base`

**Exports:**
- Model classes

**Relationships:**
- Uses: connection.Base
- Currently minimal usage

---

## Toolsmith Infrastructure - Additional Files

### `flexiai/toolsmith/tools_infrastructure/csv_helpers.py`
**Purpose:** Utility class for CSV operations (used by tools_manager for subscriber management)

**Imports:**
- `os`, `pandas`, `logging` (stdlib)

**Exports:**
- `CSVHelpers` class

**Relationships:**
- Used by: `tools_manager.py` (for identify_subscriber, retrieve_billing_details, manage_services)

**Key Methods:**
- `handle_csv()` - Dispatcher for CSV operations (read/write/update)
- `clean_dataframe()` - Cleans DataFrame (strip, lowercase)
- `find_matching_records()` - Finds records matching search criteria

---

### `flexiai/toolsmith/tools_infrastructure/security_audit.py`
**Purpose:** System security auditing tool

**Imports:**
- `subprocess`, `os`, `logging` (stdlib)
- Other security-related imports

**Exports:**
- `SecurityAudit` class
- `security_audit_dispatcher()` function

**Relationships:**
- Used by: `tools_manager.py` (for security_audit tool)

---

### `flexiai/toolsmith/_recycle/` (Experimental/In Development)

**Files:**
- `ocr_utils.py` - OCR utilities for code editor screenshots (optimized pipeline)
- `test_ocr.py` - OCR testing utilities

**Purpose:** OCR functionality (marked as "Coming Soon" in README)

**Note:** Files in `_recycle/` folder are experimental/in development and not fully integrated.

**Relationships:**
- Not currently used by main application
- Prepared for future OCR tool integration

---

## Utils Module

### `flexiai/utils/context_utils.py`
**Purpose:** Context management utilities - Token counting and truncation

**Imports:**
- `logging`
- `tiktoken`

**Exports:**
- `return_context()` function - Truncates text to fit token limits

**Relationships:**
- Used by: `tool_call_executor.py` (to truncate tool outputs)

**Key Functions:**
- `return_context(text, max_tokens, model)` - Truncates text to max_tokens for specified model
- Uses tiktoken for accurate token counting
- Preserves end of text when truncating (keeps most recent context)

---

## Summary of Import Patterns

### Most Imported Modules
1. `flexiai.core.handlers.run_thread_manager` - Used by controllers, tools_manager, event_handler
2. `flexiai.toolsmith.tools_manager` - Used by controllers, tools_registry
3. `flexiai.config.models` - Used by most modules
4. `flexiai.core.events.event_bus` - Used by controllers, event_handler, channels
5. `flexiai.channels.channel_manager` - Used by controllers, multi_channel_publisher

### External Dependencies
- `openai` - AI client
- `quart` - Web framework
- `pandas` - CSV operations
- `openpyxl` - Spreadsheet operations
- `redis` - Redis channel
- `pydantic` - Settings and models
- `sqlalchemy` - Database

---

This detailed mapping shows exact relationships between all files in the codebase.
