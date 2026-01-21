# FlexiAI Toolsmith - Project Workflow & File Relations

This document provides a detailed project workflow showing how each file relates to others and the complete flow of execution through the system.

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [File Relations by Module](#file-relations-by-module)
3. [Complete Execution Workflows](#complete-execution-workflows)
4. [File Dependency Chains](#file-dependency-chains)
5. [Data Flow Diagrams](#data-flow-diagrams)

---

## Workflow Overview

The FlexiAI Toolsmith application follows this high-level workflow:

```
1. Application Startup
   ↓
2. Configuration Loading
   ↓
3. Client Initialization
   ↓
4. Controller Setup
   ↓
5. User Interaction Loop
   ↓
6. Event Processing
   ↓
7. Tool Execution (if needed)
   ↓
8. Response Publishing
```

---

## File Relations by Module

### 1. Entry Points

#### `app.py` (Web Entry Point)
**Relations:**
- **Imports from:**
  - `flexiai.config.models.GeneralSettings` → Loads environment settings
  - `flexiai.config.logging_config.setup_logging` → Configures logging
  - `flexiai.controllers.quart_chat_controller` → Registers Blueprint routes
- **Calls:**
  - `setup_logging()` → Initializes logging system
  - `GeneralSettings()` → Loads configuration from .env
  - `qcc.QuartChatController.create_async()` → Initializes web controller
  - `app.register_blueprint()` → Mounts chat routes
- **Used by:**
  - Hypercorn server (production)
  - Direct execution (development)
- **Workflow Position:** Entry point → Initializes web server → Sets up controller

#### `chat.py` (CLI Entry Point)
**Relations:**
- **Imports from:**
  - `flexiai.config.models.GeneralSettings` → Loads environment settings
  - `flexiai.config.logging_config.setup_logging` → Configures logging
  - `flexiai.controllers.cli_chat_controller.CLIChatController` → CLI controller
- **Calls:**
  - `setup_logging()` → Initializes logging
  - `GeneralSettings()` → Loads configuration
  - `CLIChatController.create_async()` → Creates CLI controller
  - `chat_controller.run_chat_loop()` → Starts interactive loop
- **Used by:**
  - Direct execution (`python chat.py`)
- **Workflow Position:** Entry point → Initializes CLI → Starts chat loop

---

### 2. Configuration Module

#### `flexiai/config/models.py`
**Relations:**
- **Imports from:**
  - `pydantic_settings.BaseSettings` → Base for settings classes
  - `pydantic.Field` → Field definitions
- **Exports:**
  - `OpenAISettings`, `AzureOpenAISettings`, `DeepSeekSettings`, `QwenSettings`, `GitHubAzureInferenceSettings`, `GeneralSettings`
- **Used by:**
  - `flexiai/config/client_settings.py` → Validates provider settings
  - `flexiai/channels/channel_manager.py` → Reads ACTIVE_CHANNELS
  - `flexiai/controllers/*` → Reads ASSISTANT_ID, USER_ID, etc.
- **Workflow Position:** First in config chain → Defines all environment variables

#### `flexiai/config/client_settings.py`
**Relations:**
- **Imports from:**
  - `flexiai.config.models.*` → All Settings classes
- **Exports:**
  - `config` dict → Validated settings
- **Used by:**
  - `flexiai/credentials/credentials.py` → Gets provider configuration
- **Workflow Position:** Second in config chain → Validates and loads provider settings

#### `flexiai/config/client_factory.py`
**Relations:**
- **Imports from:**
  - `flexiai.credentials.credentials.get_client` → Unified client getter
- **Exports:**
  - `get_client()` → Synchronous client factory
  - `get_client_async()` → Asynchronous client factory
- **Used by:**
  - `flexiai/controllers/cli_chat_controller.py` → Gets AI client
  - `flexiai/controllers/quart_chat_controller.py` → Gets AI client
- **Workflow Position:** Third in config chain → Creates singleton AI client

#### `flexiai/config/logging_config.py`
**Relations:**
- **Imports from:**
  - `logging`, `os` (stdlib)
- **Exports:**
  - `setup_logging()` → Configures logging
- **Used by:**
  - `app.py` → Sets up web logging
  - `chat.py` → Sets up CLI logging
- **Workflow Position:** Independent → Configures logging system

---

### 3. Credentials Module

#### `flexiai/credentials/credentials.py`
**Relations:**
- **Imports from:**
  - `flexiai.config.client_settings.config` → Gets provider config
  - `openai` → OpenAI client library
- **Exports:**
  - `get_client()` → Returns configured OpenAI-compatible client
- **Used by:**
  - `flexiai/config/client_factory.py` → Creates client instance
- **Workflow Position:** Fourth in config chain → Creates actual AI client

---

### 4. Controllers Module

#### `flexiai/controllers/cli_chat_controller.py`
**Relations:**
- **Imports from:**
  - `flexiai.config.client_factory.get_client_async` → Gets AI client
  - `flexiai.core.handlers.run_thread_manager.RunThreadManager` → Manages threads
  - `flexiai.toolsmith.tools_manager.ToolsManager` → Manages tools
  - `flexiai.core.handlers.handler_factory.create_event_handler` → Creates event handler
  - `flexiai.core.events.event_bus.global_event_bus` → Event pub/sub
  - `flexiai.channels.channel_manager.get_active_channels` → Gets channels
  - `flexiai.channels.multi_channel_publisher.MultiChannelPublisher` → Publishes events
- **Exports:**
  - `CLIChatController` class
- **Used by:**
  - `chat.py` → Main CLI entry point
- **Creates:**
  - `RunThreadManager` instance
  - `ToolsManager` instance (which creates `ToolsRegistry`)
  - `EventHandler` instance (via factory)
  - Channel instances (via `get_active_channels()`)
- **Workflow Position:** Main CLI orchestrator → Coordinates all components

#### `flexiai/controllers/quart_chat_controller.py`
**Relations:**
- **Imports from:**
  - `flexiai.config.models.GeneralSettings` → Reads settings
  - `flexiai.config.client_factory.get_client_async` → Gets AI client
  - `flexiai.core.handlers.run_thread_manager.RunThreadManager` → Manages threads
  - `flexiai.toolsmith.tools_manager.ToolsManager` → Manages tools
  - `flexiai.core.events.event_bus.global_event_bus` → Event pub/sub
  - `flexiai.core.events.sse_manager.SSEManager` → SSE management
  - `flexiai.core.handlers.handler_factory.create_event_handler` → Creates event handler
  - `quart` → Web framework
- **Exports:**
  - `QuartChatController` class
  - `chat_bp` Blueprint
  - `controller_instance` (singleton)
- **Used by:**
  - `app.py` → Registers Blueprint, initializes controller
- **Creates:**
  - Similar to CLI controller but with SSE support
- **Workflow Position:** Main web orchestrator → Coordinates all components + SSE

---

### 5. Core Handlers Module

#### `flexiai/core/handlers/run_thread_manager.py`
**Relations:**
- **Imports from:**
  - OpenAI client (passed in constructor)
- **Exports:**
  - `RunThreadManager` class
- **Used by:**
  - `flexiai/controllers/cli_chat_controller.py` → Manages threads
  - `flexiai/controllers/quart_chat_controller.py` → Manages threads
  - `flexiai/core/handlers/event_handler.py` → Creates runs, submits tool outputs
  - `flexiai/toolsmith/tools_manager.py` → Creates threads for agent coordination
- **Methods called by:**
  - `get_or_create_thread()` → Creates/retrieves thread
  - `add_message_to_thread()` → Adds user messages
  - `create_run()` → Starts assistant run
  - `get_run_status()` → Checks run status
  - `get_messages()` → Retrieves messages
  - `submit_tool_outputs()` → Submits tool results
- **Workflow Position:** Thread/Run manager → Direct OpenAI API interaction

#### `flexiai/core/handlers/event_handler.py`
**Relations:**
- **Imports from:**
  - `flexiai.core.handlers.tool_call_executor.ToolCallExecutor` → Executes tools
  - `flexiai.core.handlers.run_thread_manager.RunThreadManager` → Manages runs
  - `flexiai.core.handlers.event_dispatcher.EventDispatcher` → Routes events
  - `flexiai.core.events.event_models.MessageDeltaEvent` → Event models
  - `flexiai.channels.multi_channel_publisher.MultiChannelPublisher` → Publishes events
  - `flexiai.core.events.rolling_event_buffer.RollingEventBuffer` → Event buffer
  - `flexiai.core.events.session.ChatSession` → Session management
- **Exports:**
  - `EventHandler` class
- **Used by:**
  - `flexiai/controllers/cli_chat_controller.py` → Processes events
  - `flexiai/controllers/quart_chat_controller.py` → Processes events
- **Creates:**
  - `EventDispatcher` instance
  - `ToolCallExecutor` instance
  - `MultiChannelPublisher` instance
- **Calls:**
  - `start_run()` → Starts assistant run
  - `handle_streaming_events()` → Processes event stream
  - `_handle_message_delta()` → Processes message deltas
  - `_handle_tool_call()` → Handles tool calls
- **Workflow Position:** Event processor → Central event handling hub

#### `flexiai/core/handlers/event_dispatcher.py`
**Relations:**
- **Imports from:**
  - `flexiai.core.events.event_models.*` → Event type definitions
- **Exports:**
  - `EventDispatcher` class
- **Used by:**
  - `flexiai/core/handlers/event_handler.py` → Routes events to handlers
- **Workflow Position:** Event router → Maps event types to handlers

#### `flexiai/core/handlers/handler_factory.py`
**Relations:**
- **Imports from:**
  - `flexiai.core.handlers.event_handler.EventHandler` → Event handler class
  - `flexiai.core.handlers.run_thread_manager.RunThreadManager` → Thread manager
  - `flexiai.core.handlers.event_dispatcher.EventDispatcher` → Event dispatcher
- **Exports:**
  - `create_event_handler()` function
- **Used by:**
  - `flexiai/controllers/cli_chat_controller.py` → Creates event handler
  - `flexiai/controllers/quart_chat_controller.py` → Creates event handler
- **Workflow Position:** Factory → Creates and wires EventHandler

#### `flexiai/core/handlers/tool_call_executor.py`
**Relations:**
- **Imports from:**
  - `flexiai.toolsmith.tools_registry.ToolsRegistry` → Gets tools
  - `flexiai.utils.context_utils.return_context` → Truncates outputs
- **Exports:**
  - `ToolCallExecutor` class
- **Used by:**
  - `flexiai/core/handlers/event_handler.py` → Executes tool calls
- **Calls:**
  - `execute()` → Executes tool call
  - `_execute_tool()` → Internal tool execution
  - `return_context()` → Truncates tool output to fit token limits
- **Workflow Position:** Tool executor → Executes tools from registry

---

### 6. Core Events Module

#### `flexiai/core/events/event_models.py`
**Relations:**
- **Imports from:**
  - `pydantic.BaseModel` → Event model base
- **Exports:**
  - Event model classes (MessageDeltaEvent, ThreadRunEvent, ToolCallEvent, etc.)
- **Used by:**
  - `flexiai/core/handlers/event_handler.py` → Event processing
  - `flexiai/core/handlers/event_dispatcher.py` → Event routing
  - `flexiai/channels/*` → Event publishing
- **Workflow Position:** Event definitions → Used throughout event system

#### `flexiai/core/events/event_bus.py`
**Relations:**
- **Exports:**
  - `global_event_bus` instance (singleton)
  - `EventBus` class
- **Used by:**
  - `flexiai/controllers/cli_chat_controller.py` → Subscribes to events
  - `flexiai/controllers/quart_chat_controller.py` → Subscribes to events
  - `flexiai/core/handlers/event_handler.py` → Publishes events
  - `flexiai/channels/*` → Publishes events
- **Workflow Position:** Event pub/sub hub → Central event distribution

#### `flexiai/core/events/sse_manager.py`
**Relations:**
- **Exports:**
  - `SSEManager` class
  - `global_sse_manager` instance
- **Used by:**
  - `flexiai/channels/quart_channel.py` → Sends SSE events
  - `flexiai/controllers/quart_chat_controller.py` → Manages SSE clients
- **Workflow Position:** SSE manager → Web event streaming

#### `flexiai/core/events/session.py`
**Relations:**
- **Imports from:**
  - `flexiai.core.events.rolling_event_buffer.RollingEventBuffer` → Event buffer
- **Exports:**
  - `ChatSession` class
- **Used by:**
  - `flexiai/core/handlers/event_handler.py` → Session management
- **Workflow Position:** Session manager → Maintains chat session state

#### `flexiai/core/events/rolling_event_buffer.py`
**Relations:**
- **Exports:**
  - `RollingEventBuffer` class
- **Used by:**
  - `flexiai/core/events/session.py` → Event history
- **Workflow Position:** Event buffer → Maintains recent event history

---

### 7. Channels Module

#### `flexiai/channels/base_channel.py`
**Relations:**
- **Exports:**
  - `BaseChannel` abstract class
- **Inherited by:**
  - `flexiai/channels/cli_channel.py`
  - `flexiai/channels/quart_channel.py`
  - `flexiai/channels/redis_channel.py`
- **Workflow Position:** Base class → Defines channel interface

#### `flexiai/channels/cli_channel.py`
**Relations:**
- **Imports from:**
  - `flexiai.channels.base_channel.BaseChannel` → Base class
- **Exports:**
  - `CLIChannel` class
- **Used by:**
  - `flexiai/channels/channel_manager.py` → Creates instance
  - `flexiai/channels/multi_channel_publisher.py` → Publishes events
- **Workflow Position:** CLI output → Prints events to console

#### `flexiai/channels/quart_channel.py`
**Relations:**
- **Imports from:**
  - `flexiai.channels.base_channel.BaseChannel` → Base class
  - `flexiai.core.events.sse_manager.global_sse_manager` → SSE manager
  - `quart` → Web framework
- **Exports:**
  - `QuartChannel` class
- **Used by:**
  - `flexiai/channels/channel_manager.py` → Creates instance
  - `flexiai/channels/multi_channel_publisher.py` → Publishes events
- **Workflow Position:** Web output → Sends events via SSE

#### `flexiai/channels/redis_channel.py`
**Relations:**
- **Imports from:**
  - `flexiai.channels.base_channel.BaseChannel` → Base class
  - `redis` → Redis client
- **Exports:**
  - `RedisChannel` class
- **Used by:**
  - `flexiai/channels/channel_manager.py` → Creates instance
  - `flexiai/channels/multi_channel_publisher.py` → Publishes events
- **Workflow Position:** Redis output → Publishes to Redis Pub/Sub

#### `flexiai/channels/channel_manager.py`
**Relations:**
- **Imports from:**
  - `flexiai.config.models.GeneralSettings` → Reads ACTIVE_CHANNELS
  - `flexiai.channels.cli_channel.CLIChannel` → CLI channel
  - `flexiai.channels.redis_channel.RedisChannel` → Redis channel
  - `flexiai.channels.quart_channel.QuartChannel` → Quart channel
- **Exports:**
  - `get_active_channels()` function
- **Used by:**
  - `flexiai/channels/multi_channel_publisher.py` → Gets channels
  - `flexiai/controllers/*` → Gets active channels
- **Workflow Position:** Channel factory → Creates active channels

#### `flexiai/channels/multi_channel_publisher.py`
**Relations:**
- **Imports from:**
  - `flexiai.channels.channel_manager.get_active_channels` → Gets channels
- **Exports:**
  - `MultiChannelPublisher` class
- **Used by:**
  - `flexiai/core/handlers/event_handler.py` → Publishes to all channels
- **Workflow Position:** Multi-channel publisher → Publishes to all active channels

---

### 8. Toolsmith Module

#### `flexiai/toolsmith/tools_manager.py`
**Relations:**
- **Imports from:**
  - `flexiai.core.handlers.run_thread_manager.RunThreadManager` → Thread management
  - `flexiai.toolsmith.tools_infrastructure.csv_helpers.CSVHelpers` → CSV utilities
  - `flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.*` → Spreadsheet operations
  - `flexiai.toolsmith.tools_infrastructure.csv_infrastructure.csv_entrypoint.csv_entrypoint` → CSV operations
  - `flexiai.toolsmith.tools_infrastructure.security_audit.SecurityAudit` → Security audit
- **Exports:**
  - `ToolsManager` class
- **Used by:**
  - `flexiai/toolsmith/tools_registry.py` → Registers tools
  - `flexiai/controllers/*` → Provides tool implementations
- **Creates:**
  - `ToolsRegistry` instance (if not provided)
  - `CSVHelpers` instance
  - `SecurityAudit` instance
- **Workflow Position:** Tool implementations → Core tool functionality

#### `flexiai/toolsmith/tools_registry.py`
**Relations:**
- **Imports from:**
  - `flexiai.toolsmith.tools_manager.ToolsManager` → Tool implementations
- **Exports:**
  - `ToolsRegistry` class
- **Used by:**
  - `flexiai/core/handlers/tool_call_executor.py` → Gets tools by name
- **Calls:**
  - `map_core_tools()` → Registers core tools
  - `get_tool()` → Retrieves tool by name
- **Workflow Position:** Tool registry → Maps tool names to implementations

---

### 9. Tool Infrastructure

#### CSV Infrastructure
**File Relations:**
- `csv_entrypoint.py` → Uses all CSV operations → Used by `tools_manager.py`
- `managers/csv_manager.py` → Core CSV operations → Used by all CSV operations
- `operations/*.py` → Use csv_manager, utils, exceptions → Used by csv_entrypoint
- `utils/*.py` → Utilities → Used by operations and managers
- `exceptions/csv_exceptions.py` → Exception definitions → Used by all CSV modules

#### Spreadsheet Infrastructure
**File Relations:**
- `spreadsheet_entrypoint.py` → Uses all spreadsheet operations → Used by `tools_manager.py`
- `managers/spreadsheet_manager.py` → Core spreadsheet operations → Used by all spreadsheet operations
- `operations/*.py` → Use spreadsheet_manager, utils, exceptions → Used by spreadsheet_entrypoint
- `utils/*.py` → Utilities → Used by operations and managers
- `exceptions/spreadsheet_exceptions.py` → Exception definitions → Used by all spreadsheet modules

#### Other Infrastructure
- `csv_helpers.py` → Used by `tools_manager.py` → Subscriber management
- `security_audit.py` → Used by `tools_manager.py` → Security auditing

---

### 10. Utils Module

#### `flexiai/utils/context_utils.py`
**Relations:**
- **Imports from:**
  - `tiktoken` → Token counting
- **Exports:**
  - `return_context()` function
- **Used by:**
  - `flexiai/core/handlers/tool_call_executor.py` → Truncates tool outputs
- **Workflow Position:** Context utility → Prevents token limit errors

---

## Complete Execution Workflows

### Workflow 1: Application Startup (CLI)

```
1. chat.py
   ├→ setup_logging() [logging_config.py]
   │   └→ Configures file and console logging
   │
   ├→ GeneralSettings() [config/models.py]
   │   └→ Loads .env file
   │   └→ Validates required settings
   │
   └→ CLIChatController.create_async() [controllers/cli_chat_controller.py]
       ├→ get_client_async() [config/client_factory.py]
       │   └→ get_client() [credentials/credentials.py]
       │       └→ config [config/client_settings.py]
       │           └→ models.*Settings [config/models.py]
       │
       ├→ RunThreadManager(client) [core/handlers/run_thread_manager.py]
       │   └→ Stores OpenAI client reference
       │
       ├→ ToolsManager(client, run_thread_manager) [toolsmith/tools_manager.py]
       │   ├→ Creates ToolsRegistry [toolsmith/tools_registry.py]
       │   │   └→ Maps all tools from ToolsManager
       │   ├→ Creates CSVHelpers [toolsmith/tools_infrastructure/csv_helpers.py]
       │   └→ Creates SecurityAudit [toolsmith/tools_infrastructure/security_audit.py]
       │
       ├→ create_event_handler() [core/handlers/handler_factory.py]
       │   └→ EventHandler(...) [core/handlers/event_handler.py]
       │       ├→ Creates EventDispatcher [core/handlers/event_dispatcher.py]
       │       ├→ Creates ToolCallExecutor [core/handlers/tool_call_executor.py]
       │       │   └→ Uses ToolsRegistry
       │       └→ Creates MultiChannelPublisher [channels/multi_channel_publisher.py]
       │           └→ get_active_channels() [channels/channel_manager.py]
       │               └→ Creates CLIChannel [channels/cli_channel.py]
       │
       └→ get_or_create_thread() [core/handlers/run_thread_manager.py]
           └→ Creates OpenAI thread via API

2. run_chat_loop() [controllers/cli_chat_controller.py]
   └→ Starts interactive loop
```

### Workflow 2: Application Startup (Web)

```
1. app.py
   ├→ setup_logging() [logging_config.py]
   ├→ GeneralSettings() [config/models.py]
   ├→ Quart(app) → Creates web app
   ├→ register_blueprint(qcc.chat_bp) [controllers/quart_chat_controller.py]
   │   └→ Registers /chat routes
   │
   └→ @before_serving → initialize_controller()
       └→ QuartChatController.create_async() [controllers/quart_chat_controller.py]
           └→ (Similar initialization to CLI, but with SSE support)
           └→ Creates SSEManager [core/events/sse_manager.py]
```

### Workflow 3: User Message Processing (CLI)

```
1. User Input
   ↓
2. CLIChatController.process_user_message() [controllers/cli_chat_controller.py]
   ├→ Resets event_queue
   │
   ├→ run_thread_manager.add_message_to_thread() [core/handlers/run_thread_manager.py]
   │   └→ OpenAI API: Adds message to thread
   │
   └→ event_handler.start_run() [core/handlers/event_handler.py]
       └→ run_thread_manager.create_run() [core/handlers/run_thread_manager.py]
           └→ OpenAI API: Starts assistant run
       │
       └→ handle_streaming_events() [core/handlers/event_handler.py]
           └→ For each event from OpenAI stream:
               │
               ├→ event_dispatcher.dispatch() [core/handlers/event_dispatcher.py]
               │   └→ Routes to appropriate handler
               │
               ├→ _handle_message_delta() [core/handlers/event_handler.py]
               │   └→ Creates MessageDeltaEvent [core/events/event_models.py]
               │   └→ multi_channel_publisher.publish() [channels/multi_channel_publisher.py]
               │       └→ cli_channel.publish_event() [channels/cli_channel.py]
               │           └→ Prints to console
               │
               ├→ _handle_tool_call() [core/handlers/event_handler.py]
               │   └→ tool_call_executor.execute() [core/handlers/tool_call_executor.py]
               │       ├→ tools_registry.get_tool() [toolsmith/tools_registry.py]
               │       │   └→ Returns tool function from ToolsManager
               │       │
               │       ├→ Executes tool function [toolsmith/tools_manager.py]
               │       │   └→ May call infrastructure modules:
               │       │       ├→ csv_entrypoint() [toolsmith/tools_infrastructure/csv_infrastructure/csv_entrypoint.py]
               │       │       ├→ spreadsheet_entrypoint() [toolsmith/tools_infrastructure/spreadsheet_infrastructure/spreadsheet_entrypoint.py]
               │       │       └→ security_audit() [toolsmith/tools_infrastructure/security_audit.py]
               │       │
               │       └→ return_context() [utils/context_utils.py]
               │           └→ Truncates output to fit token limits
               │
               └→ run_thread_manager.submit_tool_outputs() [core/handlers/run_thread_manager.py]
                   └→ OpenAI API: Submits tool results
                   └→ Assistant continues with tool results
```

### Workflow 4: User Message Processing (Web)

```
1. HTTP POST /chat/message
   ↓
2. QuartChatController.process_user_message() [controllers/quart_chat_controller.py]
   ├→ Gets user_id from g.user_id
   ├→ Creates thread if needed [core/handlers/run_thread_manager.py]
   ├→ Sets event_handler.current_user_id
   ├→ Resets event_queue and event_buffer
   │
   └→ (Similar to CLI flow, but...)
       └→ Events go to:
           ├→ event_buffer (buffered until client ready)
           └→ SSEManager.send_event() [core/events/sse_manager.py]
               └→ Streams to browser via SSE
```

### Workflow 5: Tool Execution Flow

```
1. AI Assistant requests tool (via OpenAI API)
   ↓
2. EventHandler receives tool_call event [core/handlers/event_handler.py]
   ↓
3. ToolCallExecutor.execute() [core/handlers/tool_call_executor.py]
   ├→ tools_registry.get_tool(tool_name) [toolsmith/tools_registry.py]
   │   └→ Returns callable from ToolsManager
   │
   ├→ Executes tool function [toolsmith/tools_manager.py]
   │   └→ Tool may call:
   │       ├→ csv_entrypoint() [csv_infrastructure/csv_entrypoint.py]
   │       │   └→ Routes to CSV operations
   │       │       └→ csv_manager [csv_infrastructure/managers/csv_manager.py]
   │       │
   │       ├→ spreadsheet_entrypoint() [spreadsheet_infrastructure/spreadsheet_entrypoint.py]
   │       │   └→ Routes to spreadsheet operations
   │       │       └→ spreadsheet_manager [spreadsheet_infrastructure/managers/spreadsheet_manager.py]
   │       │
   │       ├→ csv_helpers [toolsmith/tools_infrastructure/csv_helpers.py]
   │       │   └→ For subscriber management
   │       │
   │       └→ security_audit [toolsmith/tools_infrastructure/security_audit.py]
   │
   ├→ return_context(result) [utils/context_utils.py]
   │   └→ Truncates if exceeds token limit
   │
   └→ Returns result to EventHandler
       ↓
4. run_thread_manager.submit_tool_outputs() [core/handlers/run_thread_manager.py]
   └→ OpenAI API: Submits tool results
   └→ Assistant receives results and continues
```

---

## File Dependency Chains

### Configuration Chain
```
.env file
  ↓
flexiai/config/models.py (reads .env)
  ↓
flexiai/config/client_settings.py (validates models)
  ↓
flexiai/credentials/credentials.py (uses config)
  ↓
flexiai/config/client_factory.py (uses credentials)
  ↓
flexiai/controllers/* (uses client_factory)
```

### Event Processing Chain
```
OpenAI API Stream
  ↓
flexiai/core/handlers/run_thread_manager.py (receives stream)
  ↓
flexiai/core/handlers/event_handler.py (processes events)
  ├→ flexiai/core/handlers/event_dispatcher.py (routes events)
  ├→ flexiai/core/handlers/tool_call_executor.py (executes tools)
  │   └→ flexiai/toolsmith/tools_registry.py (gets tools)
  │       └→ flexiai/toolsmith/tools_manager.py (tool implementations)
  │           └→ Infrastructure modules (CSV/Spreadsheet/Security)
  └→ flexiai/channels/multi_channel_publisher.py (publishes events)
      └→ flexiai/channels/channel_manager.py (gets channels)
          └→ Individual channels (CLI/Quart/Redis)
              └→ flexiai/core/events/event_bus.py (event distribution)
```

### Tool Execution Chain
```
AI Assistant Tool Call
  ↓
flexiai/core/handlers/event_handler.py
  ↓
flexiai/core/handlers/tool_call_executor.py
  ↓
flexiai/toolsmith/tools_registry.py
  ↓
flexiai/toolsmith/tools_manager.py
  ├→ CSV: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/csv_entrypoint.py
  │   └→ Operations → Managers → Utils
  ├→ Spreadsheet: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/spreadsheet_entrypoint.py
  │   └→ Operations → Managers → Utils
  └→ Security: flexiai/toolsmith/tools_infrastructure/security_audit.py
  ↓
Result → flexiai/utils/context_utils.py (truncate if needed)
  ↓
flexiai/core/handlers/run_thread_manager.py (submit to OpenAI)
```

---

## Data Flow Diagrams

### Complete Request Flow (Web)

```
Browser
  ↓ HTTP POST /chat/message
app.py
  ↓
quart_chat_controller.py (process_user_message)
  ↓
run_thread_manager.py (add_message_to_thread)
  ↓ OpenAI API
OpenAI Assistant API
  ↓ Streaming Events
event_handler.py (handle_streaming_events)
  ├→ event_dispatcher.py (route event)
  ├→ tool_call_executor.py (if tool call)
  │   └→ tools_registry.py → tools_manager.py → infrastructure
  └→ multi_channel_publisher.py
      └→ quart_channel.py
          └→ sse_manager.py
              ↓ SSE Stream
Browser (receives events)
```

### Complete Request Flow (CLI)

```
User Input
  ↓
chat.py
  ↓
cli_chat_controller.py (process_user_message)
  ↓
run_thread_manager.py (add_message_to_thread)
  ↓ OpenAI API
OpenAI Assistant API
  ↓ Streaming Events
event_handler.py (handle_streaming_events)
  ├→ event_dispatcher.py (route event)
  ├→ tool_call_executor.py (if tool call)
  │   └→ tools_registry.py → tools_manager.py → infrastructure
  └→ multi_channel_publisher.py
      └→ cli_channel.py
          ↓ Print to Console
User (sees output)
```

---

## Key File Interaction Patterns

### Pattern 1: Factory Pattern
- `client_factory.py` → Creates singleton client
- `handler_factory.py` → Creates EventHandler with dependencies
- `channel_manager.py` → Creates channel instances

### Pattern 2: Registry Pattern
- `tools_registry.py` → Maps tool names to implementations
- `event_dispatcher.py` → Maps event types to handlers

### Pattern 3: Publisher-Subscriber Pattern
- `event_bus.py` → Central pub/sub system
- Controllers subscribe to events
- EventHandler publishes events
- Channels receive events

### Pattern 4: Chain of Responsibility
- `csv_entrypoint.py` → Routes to operations
- `spreadsheet_entrypoint.py` → Routes to operations
- Operations → Managers → Utils

### Pattern 5: Singleton Pattern
- `global_event_bus` → Single event bus instance
- `global_sse_manager` → Single SSE manager instance
- `controller_instance` → Single Quart controller instance

---

## Summary

This document provides a complete view of:
1. **File Relations**: How each file connects to others
2. **Execution Workflows**: Step-by-step flow through the system
3. **Dependency Chains**: How dependencies flow through modules
4. **Data Flow**: How data moves through the system
5. **Interaction Patterns**: Common design patterns used

Use this document to understand:
- Where to make changes
- How components interact
- The complete flow from user input to response
- Dependencies between modules
- How to extend the system
