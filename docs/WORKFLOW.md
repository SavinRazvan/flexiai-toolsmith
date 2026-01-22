# FlexiAI Toolsmith - Execution Workflows

This document describes the detailed execution workflows for FlexiAI Toolsmith, including startup sequences, message processing, tool execution, and streaming behavior.

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [CLI Startup Flow](#cli-startup-flow)
3. [Web Startup Flow](#web-startup-flow)
4. [CLI Message Processing](#cli-message-processing)
5. [Web Message Processing](#web-message-processing)
6. [Tool Execution Flow](#tool-execution-flow)
7. [Streaming Behavior](#streaming-behavior)
8. [File Dependency Chains](#file-dependency-chains)

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

## CLI Startup Flow

### Sequence Diagram

```
chat.py
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

### Key Steps

1. **Logging Setup** - Configures file and console logging
2. **Configuration Loading** - Loads and validates `.env` settings
3. **Client Creation** - Initializes AI provider client (OpenAI/Azure/etc.)
4. **Thread Manager** - Sets up thread and run management
5. **Tool Infrastructure** - Initializes tool registry and managers
6. **Event Handler** - Creates event processing pipeline
7. **Channel Setup** - Configures output channels (CLI in this case)
8. **Thread Creation** - Creates or retrieves OpenAI Assistant thread
9. **Chat Loop** - Starts interactive terminal interface

---

## Web Startup Flow

### Sequence Diagram

```
app.py
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

### Key Differences from CLI

- **Quart Application** - Web server initialization
- **Blueprint Registration** - Route mounting for `/chat` endpoints
- **SSE Manager** - Server-Sent Events for real-time streaming
- **Session Management** - User session handling via cookies/sessions
- **Async Initialization** - Controller setup in `@before_serving` hook

---

## CLI Message Processing

### Complete Flow

```
1. User Input (terminal)
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
               │       │       ├→ csv_entrypoint() [csv_infrastructure]
               │       │       ├→ spreadsheet_entrypoint() [spreadsheet_infrastructure]
               │       │       └→ security_audit() [security_audit]
               │       │
               │       └→ return_context() [utils/context_utils.py]
               │           └→ Truncates output to fit token limits
               │
               └→ run_thread_manager.submit_tool_outputs() [core/handlers/run_thread_manager.py]
                   └→ OpenAI API: Submits tool results
                   └→ Assistant continues with tool results
```

### Key Characteristics

- **Synchronous Terminal Output** - Events printed directly to console
- **Real-time Streaming** - Response chunks appear as they're generated
- **Interactive Loop** - Continuous input/output cycle
- **Direct Event Publishing** - Events go straight to CLI channel

---

## Web Message Processing

### Complete Flow

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

### Key Differences from CLI

- **HTTP Request Handling** - Quart routes handle incoming requests
- **User Session Management** - User identification via cookies/sessions
- **Event Buffering** - Events buffered for clients connecting mid-stream
- **SSE Streaming** - Server-Sent Events for real-time browser updates
- **Multi-User Support** - Concurrent sessions handled via user_id

---

## Tool Execution Flow

### Complete Sequence

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

### Tool Execution Steps

1. **Tool Call Detection** - EventHandler receives tool call from Assistant API
2. **Tool Lookup** - ToolsRegistry maps tool name to function
3. **Parameter Validation** - Tool executor validates parameters
4. **Tool Execution** - Infrastructure module performs operation
5. **Result Processing** - Output truncated if exceeds token limits
6. **Result Submission** - Results sent back to Assistant API
7. **Response Generation** - Assistant processes results and continues

---

## Streaming Behavior

### CLI Streaming

- **Real-time Output** - Text appears character-by-character or chunk-by-chunk
- **Event-Driven Updates** - Each `MessageDeltaEvent` triggers console output
- **No Buffering** - Events published immediately to terminal

### Web Streaming (SSE)

- **Server-Sent Events** - HTTP-based streaming protocol
- **Event Buffering** - Events buffered for late-connecting clients
- **Connection Management** - SSE manager tracks active connections
- **Multi-User Isolation** - Each user receives only their events

### Event Types in Stream

- **Message Delta** - Text chunks as they're generated
- **Tool Call Start** - Tool invocation begins
- **Tool Call Progress** - Tool execution updates (if supported)
- **Tool Call Complete** - Tool results available
- **Run Complete** - Assistant response finished

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

## Differences: CLI vs Web

| Aspect | CLI | Web |
|--------|-----|-----|
| **Input** | Terminal stdin | HTTP POST requests |
| **Output** | Direct console print | SSE streaming |
| **Session** | Single session | Multi-user sessions |
| **Buffering** | None | Event buffer for late clients |
| **User Management** | Environment variable | Cookies/sessions |
| **Real-time** | Immediate terminal updates | SSE chunks to browser |

---

## Observability

### Logging

**Log Levels:**
- `DEBUG` – Detailed execution flow, event processing, tool calls
- `INFO` – Application startup, configuration, major operations
- `ERROR` – Exceptions, failures, critical issues
- `WARNING` – Deprecations, configuration issues

**Log Locations:**
- File logs: `logs/app.log` (rotating, configurable)
- Console logs: Based on `console_level` in logging configuration
- Default: File logging at DEBUG, console at ERROR

**Enabling DEBUG Mode:**
```python
# In app.py or chat.py
setup_logging(
    root_level=logging.DEBUG,
    file_level=logging.DEBUG,
    console_level=logging.DEBUG,  # Enable console DEBUG
    enable_file_logging=True,
    enable_console_logging=True
)
```

### Tracing

**Correlation Flow:**
- `user_id` is stored in `EventHandler.current_user_id` and logged with operations
- `thread_id` and `assistant_id` are logged with each operation
- Tool executions include `tool_name` in logs
- Thread tracking uses `"{assistant_id}:{user_id}"` as key

**Example Log Pattern:**
```
[INFO] [start_run] assistant='asst_123' thread='thread_abc' user_id='user_xyz'
[INFO] [add_message_to_thread] Thread id: 'thread_abc' -> adding message for user_id: 'user_xyz'
[INFO] [execute] Running 'security_audit' with {'operation': 'reconnaissance'}
[DEBUG] [execute] 'security_audit' succeeded
```

**Searching Logs:**
```bash
# Find all tool executions
grep "ToolExecutor.*Executing" logs/app.log

# Find errors for a specific thread
grep "thread_abc123" logs/app.log | grep ERROR

# Find all security audit operations
grep "security_audit" logs/app.log
```

---

## Error Handling & Retry Semantics

### Failure Scenarios

#### OpenAI Streaming Fails Mid-Run

**Behavior:**
- Exception caught in `EventHandler.start_run()`
- Error logged with `logger.error()`
- `_handle_error_event()` called if error event received from stream
- User may receive partial response
- Thread remains in last known state (can be resumed)

**Retry:**
- No automatic retry by default
- User can resend message to continue
- Thread state is preserved

#### Tool Raises Exception

**Behavior:**
- `ToolCallExecutor.execute()` raises exception
- Exception caught in `EventHandler._handle_requires_action()`
- Exception converted to string: `result = str(e)`
- `prepare_tool_output()` formats error: `{"status": False, "message": str(e), "result": None}`
- Error formatted as: `{"tool_call_id": "...", "output": "{\"status\": false, \"message\": \"...\", \"result\": null}"}`
- Error is submitted to Assistant API as tool output
- Assistant can handle error and respond appropriately

**Retry:**
- No automatic retry
- Assistant can request tool again with different parameters
- Tool errors are logged with full stack trace in `logs/app.log`

#### Redis Channel Unavailable

**Behavior:**
- `ChannelManager` detects connection failure
- Falls back to available channels (CLI/Quart)
- If no channels available, error is logged and user notified
- Application continues with available channels

**Retry:**
- Redis channel attempts reconnection on next publish
- No automatic retry loop (avoids blocking)

### Error Handling Flow

```
Exception/Error
    ↓
Component catches error
    ↓
Logs error with logger.error()
    ↓
EventHandler._handle_error_event() (if from stream)
    ↓
Error logged to logs/app.log
    ↓
Tool errors returned as {"status": False, "error": "message"}
    ↓
Assistant receives error as tool output
```

### Expected Fallback Behaviors

1. **Streaming Failure:**
   - Exception caught and logged
   - `_handle_error_event()` called if error event in stream
   - User may receive partial response
   - Thread remains usable for next message

2. **Tool Exception:**
   - Exception caught in `ToolCallExecutor.execute()`
   - Error formatted via `prepare_tool_output()` with `success=False`
   - Assistant receives error as tool output: `{"status": False, "message": "...", "result": None}`
   - Assistant can respond with error context

3. **Channel Failure:**
   - System falls back to available channels (managed by `ChannelManager`)
   - Error logged if channel publish fails
   - Application continues (does not crash)
   - If no channels available, error logged but execution continues

---

## Testing Hooks

### Simulating Streaming Events

**Unit Test Example:**
```python
from flexiai.core.events.event_models import MessageDeltaEvent
from flexiai.core.handlers.event_handler import EventHandler

# Create mock stream
mock_stream = [
    MessageDeltaEvent(content="Hello", delta="Hello"),
    MessageDeltaEvent(content=" World", delta=" World")
]

# Process events
event_handler = EventHandler(...)
for event in mock_stream:
    event_handler._handle_message_delta(event)
```

### Injecting Test Clients

**Using client_factory:**
```python
from flexiai.config.client_factory import get_client_async

# Mock OpenAI client
class MockOpenAIClient:
    async def create_thread(self): ...
    async def create_run(self, thread_id, assistant_id): ...

# Inject in tests
async def test_controller():
    client = MockOpenAIClient()
    controller = await CLIChatController.create_async(
        assistant_id="test",
        user_id="test_user",
        client=client  # Inject mock
    )
```

### Mocking Tool Execution

```python
from flexiai.toolsmith.tools_registry import ToolsRegistry

# Mock tool
def mock_security_audit(operation, **kwargs):
    return {"status": True, "result": {"test": "data"}}

# Register mock
registry = ToolsRegistry(...)
registry.registered_tools["security_audit"] = mock_security_audit
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) – System architecture and components
- [TOOLING.md](TOOLING.md) – Tool capabilities and usage
- [FILE_MAPPING.md](FILE_MAPPING.md) – Detailed file reference
