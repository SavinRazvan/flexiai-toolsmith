# FlexiAI Toolsmith - Complete File Mapping & Documentation

**Internal Reference Document** – This document provides comprehensive mapping of all files in the project, including their purposes, dependencies, relationships, imports, exports, and detailed information.

> **Note:** This is a detailed internal reference for maintainers. For user-facing documentation, see [README.md](../README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [WORKFLOW.md](WORKFLOW.md).

## Table of Contents

1. [Entry Points](#entry-points)
2. [Project Structure](#project-structure)
3. [Module-by-Module File Mapping](#module-by-module-file-mapping)
4. [Detailed File Documentation](#detailed-file-documentation)
5. [Dependency Graph](#dependency-graph)
6. [Data Flow](#data-flow)
7. [Import Patterns Summary](#import-patterns-summary)

---

## Entry Points

### Root Level Entry Points

| File | Purpose | Dependencies | Used By |
|------|---------|--------------|---------|
| `app.py` | **Web Application Entry Point** - Quart web server for SSE chat interface | `flexiai.config.models`, `flexiai.config.logging_config`, `flexiai.controllers.quart_chat_controller` | Hypercorn server |
| `chat.py` | **CLI Application Entry Point** - Command-line chat interface | `flexiai.config.models`, `flexiai.config.logging_config`, `flexiai.controllers.cli_chat_controller` | Direct execution |

---

## Project Structure

```
flexiai-toolsmith/
├── app.py                          # Web entry point
├── chat.py                         # CLI entry point
├── flexiai/
│   ├── agents/                     # Multi-agent system (experimental)
│   ├── channels/                  # Event publishing channels
│   ├── config/                    # Configuration management
│   ├── controllers/               # Application controllers
│   ├── core/                      # Core event handling
│   ├── credentials/               # AI provider credentials
│   ├── database/                  # Database models & connection
│   ├── toolsmith/                 # Tool infrastructure
│   └── utils/                     # Utility functions
├── templates/                      # HTML templates
├── static/                        # Static assets
└── logs/                          # Log files
```

---

## Module-by-Module File Mapping

### 1. Configuration Module (`flexiai/config/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `models.py` | **Pydantic Settings Models** - Defines all environment variable models (OpenAI, Azure, DeepSeek, Qwen, GitHub, General) | `pydantic_settings`, `pydantic` | `OpenAISettings`, `AzureOpenAISettings`, `DeepSeekSettings`, `QwenSettings`, `GitHubAzureInferenceSettings`, `GeneralSettings` |
| `client_settings.py` | **Client Configuration** - Validates and loads provider-specific settings | `flexiai.config.models` | `config` (validated settings dict) |
| `client_factory.py` | **Client Factory** - Creates singleton AI client instances (sync/async) | `flexiai.credentials.credentials` | `get_client()`, `get_client_async()` |
| `logging_config.py` | **Logging Setup** - Configures rotating file and console logging | `logging`, `os` | `setup_logging()` |

**Relationships:**
- `models.py` → Used by `client_settings.py`
- `client_settings.py` → Used by `credentials.py`
- `client_factory.py` → Uses `credentials.py` → Used by all controllers
- `logging_config.py` → Used by `app.py`, `chat.py`

---

### 2. Credentials Module (`flexiai/credentials/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `credentials.py` | **Credential Manager** - Unified interface for all AI providers (OpenAI, Azure, DeepSeek, Qwen, GitHub) | `flexiai.config.client_settings`, `openai` | `get_client()` - Returns configured OpenAI-compatible client |

**Relationships:**
- Uses `client_settings.py` to get provider config
- Used by `client_factory.py`
- Creates the base AI client for all operations

---

### 3. Controllers Module (`flexiai/controllers/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `cli_chat_controller.py` | **CLI Chat Controller** - Manages command-line chat loop, user input/output | `flexiai.config.client_factory`, `flexiai.core.handlers.*`, `flexiai.toolsmith.tools_manager`, `flexiai.core.events.event_bus`, `flexiai.channels.*` | `CLIChatController` class |
| `quart_chat_controller.py` | **Web Chat Controller** - Manages HTTP/SSE chat sessions, Blueprint routes | `flexiai.config.*`, `flexiai.core.handlers.*`, `flexiai.toolsmith.tools_manager`, `flexiai.core.events.*`, `quart` | `QuartChatController` class, `chat_bp` Blueprint |

**Relationships:**
- Both controllers use:
  - `client_factory.py` → Get AI client
  - `run_thread_manager.py` → Manage threads/runs
  - `tools_manager.py` → Access tools
  - `handler_factory.py` → Create event handlers
  - `event_bus.py` → Publish events
  - `channel_manager.py` → Get active channels
- `cli_chat_controller.py` → Used by `chat.py`
- `quart_chat_controller.py` → Used by `app.py`

---

### 4. Core Handlers Module (`flexiai/core/handlers/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `run_thread_manager.py` | **Thread/Run Manager** - Manages OpenAI Assistant API threads, runs, messages | `openai` client | `RunThreadManager` class |
| `event_handler.py` | **Event Handler** - Processes streaming events, dispatches to handlers, manages tool calls | `flexiai.core.handlers.tool_call_executor`, `flexiai.core.handlers.run_thread_manager`, `flexiai.core.handlers.event_dispatcher`, `flexiai.core.events.*`, `flexiai.channels.multi_channel_publisher` | `EventHandler` class |
| `event_dispatcher.py` | **Event Dispatcher** - Routes events to appropriate handlers based on event type | `flexiai.core.events.event_models` | `EventDispatcher` class |
| `handler_factory.py` | **Handler Factory** - Creates EventHandler instances with proper wiring | `flexiai.core.handlers.event_handler`, `flexiai.core.handlers.run_thread_manager`, `flexiai.core.handlers.event_dispatcher` | `create_event_handler()` function |
| `tool_call_executor.py` | **Tool Call Executor** - Executes tool calls from AI assistant | `flexiai.toolsmith.tools_registry`, `flexiai.utils.context_utils` | `ToolCallExecutor` class |

**Relationships:**
- `run_thread_manager.py` → Used by all controllers, event_handler, tools_manager
- `event_handler.py` → Uses all other handlers, publishes to channels
- `event_dispatcher.py` → Used by event_handler
- `handler_factory.py` → Creates event_handler instances
- `tool_call_executor.py` → Uses tools_registry → Executes tools

---

### 5. Core Events Module (`flexiai/core/events/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `event_models.py` | **Event Models** - Pydantic models for all event types (MessageDelta, ThreadRun, etc.) | `pydantic` | Event model classes |
| `event_bus.py` | **Event Bus** - Pub/sub system for events (singleton) | None | `global_event_bus` instance |
| `sse_manager.py` | **SSE Manager** - Manages Server-Sent Events for web clients | `threading`, `collections` | `SSEManager` class, `global_sse_manager` |
| `session.py` | **Chat Session** - Manages chat session state | `flexiai.core.events.rolling_event_buffer` | `ChatSession` class |
| `rolling_event_buffer.py` | **Rolling Buffer** - Maintains rolling buffer of recent events | `collections` | `RollingEventBuffer` class |

**Relationships:**
- `event_models.py` → Used by all event-related modules
- `event_bus.py` → Used by controllers, event_handler, channels
- `sse_manager.py` → Used by quart_channel, quart_chat_controller
- `session.py` → Uses rolling_event_buffer
- All event modules → Used by event_handler

---

### 6. Channels Module (`flexiai/channels/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `base_channel.py` | **Base Channel** - Abstract base class for all channels | `abc` | `BaseChannel` abstract class |
| `cli_channel.py` | **CLI Channel** - Publishes events to console/stdout | `flexiai.channels.base_channel` | `CLIChannel` class |
| `quart_channel.py` | **Quart Channel** - Publishes events via SSE to web clients | `flexiai.channels.base_channel`, `flexiai.core.events.sse_manager`, `quart` | `QuartChannel` class |
| `redis_channel.py` | **Redis Channel** - Publishes events to Redis Pub/Sub | `flexiai.channels.base_channel`, `redis` | `RedisChannel` class |
| `channel_manager.py` | **Channel Manager** - Factory for creating active channels | `flexiai.config.models`, `flexiai.channels.*` | `get_active_channels()` function |
| `multi_channel_publisher.py` | **Multi-Channel Publisher** - Publishes to multiple channels simultaneously | `flexiai.channels.channel_manager` | `MultiChannelPublisher` class |

**Relationships:**
- `base_channel.py` → Base for all channel implementations
- `cli_channel.py`, `quart_channel.py`, `redis_channel.py` → Inherit from base_channel
- `channel_manager.py` → Creates instances based on ACTIVE_CHANNELS config
- `multi_channel_publisher.py` → Uses channel_manager → Publishes to all active channels
- All channels → Used by event_handler via multi_channel_publisher

---

### 7. Toolsmith Module (`flexiai/toolsmith/`)

#### Core Toolsmith Files

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `tools_manager.py` | **Tools Manager** - Core tool implementations (RAG, agent coordination, YouTube, CSV, Spreadsheet, Security) | `flexiai.core.handlers.run_thread_manager`, `flexiai.toolsmith.tools_infrastructure.*` | `ToolsManager` class |
| `tools_registry.py` | **Tools Registry** - Maps tool names to callable functions | `flexiai.toolsmith.tools_manager` | `ToolsRegistry` class |

**Relationships:**
- `tools_manager.py` → Uses all infrastructure modules → Provides tool implementations
- `tools_registry.py` → Uses tools_manager → Maps tools for execution
- Both → Used by controllers, tool_call_executor

#### CSV Infrastructure (`flexiai/toolsmith/tools_infrastructure/csv_infrastructure/`)

| File | Purpose | Dependencies |
|------|---------|--------------|
| `csv_entrypoint.py` | **CSV Entry Point** - Main CSV operations dispatcher | All CSV operation modules, utils, exceptions |
| `managers/csv_manager.py` | **CSV Manager** - Core CSV file operations | `pandas`, utils, exceptions |
| `operations/create_operations.py` | Create CSV files | csv_manager, utils |
| `operations/read_operations.py` | Read CSV data | csv_manager, utils |
| `operations/update_operations.py` | Update CSV rows | csv_manager, utils |
| `operations/delete_operations.py` | Delete CSV rows/files | csv_manager, utils |
| `operations/filter_operations.py` | Filter CSV rows | csv_manager, utils |
| `operations/data_validation_operations.py` | Validate CSV data | csv_manager, utils |
| `operations/data_transformation_operations.py` | Transform CSV data | csv_manager, utils |
| `utils/file_handler.py` | File path validation | exceptions |
| `utils/error_handler.py` | Error response formatting | exceptions |
| `utils/mixed_helpers.py` | Type conversion utilities | None |
| `exceptions/csv_exceptions.py` | CSV-specific exceptions | None |

**Relationships:**
- `csv_entrypoint.py` → Uses all operations → Used by tools_manager
- Operations → Use csv_manager, utils, exceptions
- Utils → Used by operations and managers

#### Spreadsheet Infrastructure (`flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/`)

| File | Purpose | Dependencies |
|------|---------|--------------|
| `spreadsheet_entrypoint.py` | **Spreadsheet Entry Point** - Main spreadsheet operations dispatcher | All spreadsheet operation modules, utils, exceptions |
| `managers/spreadsheet_manager.py` | **Spreadsheet Manager** - Core spreadsheet operations | `openpyxl`, utils, exceptions |
| `operations/file_operations.py` | Create/open/close spreadsheets | spreadsheet_manager |
| `operations/sheet_operations.py` | Sheet management | spreadsheet_manager |
| `operations/data_entry_operations.py` | Write data to cells | spreadsheet_manager |
| `operations/data_retrieval_operations.py` | Read data from cells | spreadsheet_manager |
| `operations/data_analysis_operations.py` | Analyze spreadsheet data | spreadsheet_manager |
| `operations/formula_operations.py` | Formula management | spreadsheet_manager |
| `operations/formatting_operations.py` | Cell formatting | spreadsheet_manager |
| `operations/data_validation_operations.py` | Data validation | spreadsheet_manager |
| `operations/data_transformation_operations.py` | Data transformation | spreadsheet_manager |
| `operations/chart_operations.py` | Chart creation | spreadsheet_manager |
| `utils/file_handler.py` | File path validation | exceptions |
| `utils/error_handler.py` | Error response formatting | exceptions |
| `utils/mixed_helpers.py` | Type conversion utilities | None |
| `exceptions/spreadsheet_exceptions.py` | Spreadsheet-specific exceptions | None |

**Relationships:**
- Similar structure to CSV infrastructure
- `spreadsheet_entrypoint.py` → Uses all operations → Used by tools_manager
- Operations → Use spreadsheet_manager, utils, exceptions

#### Other Infrastructure Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| `csv_helpers.py` | **CSV Helpers** - Utility class for CSV operations (subscriber management) | `pandas` |
| `security_audit.py` | **Security Audit** - System security auditing tool | `subprocess`, `os` |

**Relationships:**
- `csv_helpers.py` → Used by tools_manager (for identify_subscriber, retrieve_billing_details, manage_services)
- `security_audit.py` → Used by tools_manager (for security_audit tool)

#### Experimental/In Development

| File | Purpose | Status |
|------|---------|--------|
| `_recycle/ocr_utils.py` | **OCR Utilities** - OCR for code editor screenshots | Experimental, not integrated |
| `_recycle/test_ocr.py` | **OCR Testing** - Test utilities for OCR | Experimental, not integrated |

**Note:** Files in `_recycle/` folder are experimental and marked as "Coming Soon" in README.

---

### 8. Database Module (`flexiai/database/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `connection.py` | **Database Connection** - SQLAlchemy engine and session factory | `sqlalchemy`, `os` | `engine`, `SessionLocal`, `Base` |
| `models.py` | **Database Models** - SQLAlchemy ORM models | `sqlalchemy`, `flexiai.database.connection` | Model classes |

**Relationships:**
- `connection.py` → Sets up database → Used by models
- `models.py` → Uses connection → Defines database schema
- Currently minimal usage (prepared for future features)

---

### 9. Utils Module (`flexiai/utils/`)

| File | Purpose | Dependencies | Exports |
|------|---------|--------------|---------|
| `context_utils.py` | **Context Utilities** - Token counting and truncation | `tiktoken`, `logging` | `return_context()` function |

**Relationships:**
- Used by: `tool_call_executor.py` (to truncate tool outputs to fit token limits)

**Key Functions:**
- `return_context()` - Truncates text to max_tokens, preserving end of text (most recent context)

---

### 10. Agents Module (`flexiai/agents/`) - Experimental

This module contains experimental multi-agent system components. Files are organized into submodules:

- **`core/`** - Base agent classes, factory, registry
- **`behaviors/`** - Agent behaviors (adaptive, async, collaborative, learning)
- **`coordination/`** - Agent coordination (handoff, message broker, triage)
- **`memory/`** - Agent memory management
- **`monitoring/`** - Agent monitoring and safety
- **`specialists/`** - Specialized agent types
- **`utils/`** - Agent utilities
- **`workflows/`** - Workflow management
- **`integrations/`** - External integrations

**Note:** This module is experimental and not fully integrated into the main application flow.

---

## Detailed File Documentation

### Root Level Files

#### `app.py`
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

#### `chat.py`
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

### Configuration Module

#### `flexiai/config/models.py`
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

#### `flexiai/config/client_settings.py`
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

#### `flexiai/config/client_factory.py`
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

#### `flexiai/config/logging_config.py`
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

### Credentials Module

#### `flexiai/credentials/credentials.py`
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

### Controllers Module

#### `flexiai/controllers/cli_chat_controller.py`
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

#### `flexiai/controllers/quart_chat_controller.py`
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

### Core Handlers Module

#### `flexiai/core/handlers/run_thread_manager.py`
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

#### `flexiai/core/handlers/event_handler.py`
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

#### `flexiai/core/handlers/event_dispatcher.py`
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

#### `flexiai/core/handlers/handler_factory.py`
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

#### `flexiai/core/handlers/tool_call_executor.py`
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

### Core Events Module

#### `flexiai/core/events/event_models.py`
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

#### `flexiai/core/events/event_bus.py`
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

#### `flexiai/core/events/sse_manager.py`
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

#### `flexiai/core/events/session.py`
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

#### `flexiai/core/events/rolling_event_buffer.py`
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

### Channels Module

#### `flexiai/channels/base_channel.py`
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

#### `flexiai/channels/cli_channel.py`
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

#### `flexiai/channels/quart_channel.py`
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

#### `flexiai/channels/redis_channel.py`
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

#### `flexiai/channels/channel_manager.py`
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

#### `flexiai/channels/multi_channel_publisher.py`
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

### Toolsmith Module

#### `flexiai/toolsmith/tools_manager.py`
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

#### `flexiai/toolsmith/tools_registry.py`
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

### CSV Infrastructure

#### `flexiai/toolsmith/tools_infrastructure/csv_infrastructure/csv_entrypoint.py`
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

### Spreadsheet Infrastructure

#### `flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/spreadsheet_entrypoint.py`
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

### Additional Infrastructure Files

#### `flexiai/toolsmith/tools_infrastructure/csv_helpers.py`
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

#### `flexiai/toolsmith/tools_infrastructure/security_audit.py`
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

#### `flexiai/toolsmith/_recycle/` (Experimental/In Development)

**Files:**
- `ocr_utils.py` - OCR utilities for code editor screenshots (optimized pipeline)
- `test_ocr.py` - OCR testing utilities

**Purpose:** OCR functionality (marked as "Coming Soon" in README)

**Note:** Files in `_recycle/` folder are experimental/in development and not fully integrated.

**Relationships:**
- Not currently used by main application
- Prepared for future OCR tool integration

---

### Database Module

#### `flexiai/database/connection.py`
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

#### `flexiai/database/models.py`
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

### Utils Module

#### `flexiai/utils/context_utils.py`
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

## Dependency Graph

### High-Level Flow

```
Entry Points (app.py, chat.py)
    ↓
Controllers (CLIChatController, QuartChatController)
    ↓
Client Factory → Credentials → Client Settings → Models
    ↓
Run Thread Manager → OpenAI Client
    ↓
Tools Manager → Tools Registry
    ↓
Event Handler → Event Dispatcher → Tool Call Executor
    ↓
Multi-Channel Publisher → Channels (CLI/Quart/Redis)
    ↓
Event Bus → Event Models
```

### Detailed Dependencies

#### Configuration Chain
```
models.py
  ↓
client_settings.py
  ↓
credentials.py
  ↓
client_factory.py
  ↓
controllers
```

#### Event Flow
```
controllers
  ↓
handler_factory.py
  ↓
event_handler.py
  ├→ event_dispatcher.py
  ├→ tool_call_executor.py
  │     ↓
  │   tools_registry.py
  │     ↓
  │   tools_manager.py
  │     ↓
  │   infrastructure modules
  └→ multi_channel_publisher.py
        ↓
      channels (CLI/Quart/Redis)
        ↓
      event_bus.py
        ↓
      event_models.py
```

#### Tool Execution Flow
```
AI Assistant (via OpenAI API)
  ↓
tool_call_executor.py
  ↓
tools_registry.py
  ↓
tools_manager.py
  ├→ CSV Infrastructure
  ├→ Spreadsheet Infrastructure
  ├→ Security Audit
  └→ Core Tools (RAG, Agent Coordination, YouTube)
```

---

## Data Flow

### 1. Application Startup

**CLI (`chat.py`):**
```
chat.py
  → setup_logging()
  → GeneralSettings()
  → CLIChatController.create_async()
    → get_client_async()
      → credentials.get_client()
        → client_settings.config
          → models.*Settings
    → RunThreadManager(client)
    → ToolsManager(client, run_thread_manager)
      → ToolsRegistry(tools_manager)
    → create_event_handler()
      → EventHandler(...)
        → EventDispatcher()
        → ToolCallExecutor(tools_registry)
    → get_active_channels()
      → CLIChannel()
  → run_chat_loop()
```

**Web (`app.py`):**
```
app.py
  → setup_logging()
  → GeneralSettings()
  → Quart(app)
  → register_blueprint(quart_chat_controller.chat_bp)
  → @before_serving
    → QuartChatController.create_async()
      (similar to CLI initialization)
  → app.run()
```

### 2. User Message Flow

**CLI:**
```
User Input
  → CLIChatController.process_user_message()
    → RunThreadManager.create_message()
    → RunThreadManager.create_run()
    → EventHandler.handle_streaming_events()
      → For each event:
        → EventDispatcher.dispatch()
        → ToolCallExecutor.execute() (if tool call)
        → MultiChannelPublisher.publish()
          → CLIChannel.publish_event()
            → Print to console
```

**Web:**
```
HTTP POST /chat/message
  → QuartChatController.process_user_message()
    → Similar to CLI flow
    → QuartChannel.publish_event()
      → SSEManager.send_event()
        → SSE stream to browser
```

### 3. Tool Call Flow

```
AI Assistant requests tool
  → EventHandler receives tool_call event
    → ToolCallExecutor.execute()
      → ToolsRegistry.get_tool()
        → ToolsManager method
          → Infrastructure module (CSV/Spreadsheet/etc.)
            → Returns result
      → RunThreadManager.submit_tool_outputs()
        → AI Assistant receives result
          → Continues conversation
```

---

## Import Patterns Summary

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

## Key Relationships Summary

1. **Configuration**: `models.py` → `client_settings.py` → `credentials.py` → `client_factory.py`
2. **Controllers**: Both use `client_factory`, `run_thread_manager`, `tools_manager`, `event_handler`
3. **Event System**: `event_handler` → `event_dispatcher` → `tool_call_executor` → `tools_registry`
4. **Channels**: `multi_channel_publisher` → `channel_manager` → individual channels → `event_bus`
5. **Tools**: `tools_manager` → infrastructure modules (CSV, Spreadsheet, Security) → operations → managers → utils
6. **Thread Management**: `run_thread_manager` → OpenAI Assistant API → threads/runs/messages

---

## Non-Python Files

### Templates (`templates/`)
- `base.html` - Base template
- `index.html` - Landing page
- `chat.html` - Chat interface page
- `_chat_widget.html` - Chat widget component
- `_navbar.html` - Navigation bar component

**Relationships:**
- Used by: `app.py`, `quart_chat_controller.py` (via `render_template()`)

### Static Files (`static/`)
- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Image assets

**Relationships:**
- Served by: `app.py` (via Quart static file serving)
- Referenced by: HTML templates

### Configuration Files
- `.env` - Environment variables (git-ignored)
- `.env.template` - Environment template
- `requirements.txt` - Python dependencies
- `requirements.in` - Source dependencies
- `environment.yml` - Conda environment
- `Dockerfile` - Docker configuration

### Documentation Files
- `README.md` - Main documentation (root)
- `docs/ARCHITECTURE.md` - System architecture and design
- `docs/WORKFLOW.md` - Execution workflows and data flow
- `docs/TOOLING.md` - Tool capabilities and usage
- `docs/ENV_SETUP.md` - Environment setup guide
- `docs/FILE_MAPPING.md` - This file (detailed internal reference)

---

## File Count Summary

- **Total Python Files**: 113
- **Core Application**: ~30 files
- **Tool Infrastructure**: ~50 files
- **Agents (Experimental)**: ~30 files
- **Configuration**: 4 files
- **Controllers**: 2 files
- **Channels**: 6 files
- **Core Handlers**: 5 files
- **Core Events**: 5 files
- **Templates**: 5 HTML files
- **Static Assets**: Multiple CSS/JS/image files

---

This comprehensive mapping provides detailed information about every file in the codebase, including exact imports, exports, relationships, and data flow patterns. Use it to understand how components interact and where to make changes.
