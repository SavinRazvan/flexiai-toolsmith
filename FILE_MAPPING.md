# FlexiAI Toolsmith - File Mapping & Relationships

This document provides a comprehensive mapping of all files in the project, their purposes, dependencies, and relationships.

## Table of Contents

1. [Entry Points](#entry-points)
2. [Project Structure](#project-structure)
3. [Module-by-Module File Mapping](#module-by-module-file-mapping)
4. [Dependency Graph](#dependency-graph)
5. [Data Flow](#data-flow)

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
| `tool_call_executor.py` | **Tool Call Executor** - Executes tool calls from AI assistant | `flexiai.toolsmith.tools_registry` | `ToolCallExecutor` class |

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
- `README.md` - Main documentation
- `ENV_SETUP.md` - Environment setup guide
- `FILE_MAPPING.md` - This file
- `FILE_DETAILED_MAPPING.md` - Detailed file mapping
- `TODO.md` - Project todos

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

## Key Missing Relationships (Now Documented)

1. **`tool_call_executor.py`** → Uses `context_utils.return_context()` to truncate tool outputs
2. **`csv_helpers.py`** → Used by `tools_manager.py` for subscriber management tools
3. **`_recycle/ocr_utils.py`** → Experimental OCR functionality (not yet integrated)
4. **Templates** → Used by `app.py` and `quart_chat_controller.py`
5. **Static files** → Served by Quart app

---

This mapping provides a comprehensive view of the codebase structure and relationships. Use it to understand how components interact and where to make changes.
