# FlexiAI Toolsmith - System Architecture

This document describes the system architecture, component design, and internal structure of FlexiAI Toolsmith.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Architecture](#component-architecture)
3. [Event-Oriented Execution Pipeline](#event-oriented-execution-pipeline)
4. [Channel System](#channel-system)
5. [Provider Abstraction](#provider-abstraction)
6. [Tool Infrastructure](#tool-infrastructure)
7. [Architecture Diagrams](#architecture-diagrams)

---

## Architecture Overview

FlexiAI Toolsmith follows a **layered, modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   Entry Points                          │
│              (app.py, chat.py)                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Controllers                            │
│    (CLIChatController, QuartChatController)            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Core Handlers                              │
│  (RunThreadManager, EventHandler, ToolExecutor)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Event System                               │
│        (EventBus, SSE Manager, Channels)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Tool Infrastructure                        │
│    (ToolsRegistry, ToolsManager, Infrastructure)         │
└─────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Entry Points

**`app.py`** (Web Application)
- Quart web server initialization
- Blueprint registration for chat routes
- User session management
- Form submission handling

**`chat.py`** (CLI Application)
- CLI chat loop initialization
- Interactive terminal interface
- Direct user input/output

### Controllers

Controllers orchestrate the interaction between users and the AI assistant:

**`CLIChatController`**
- Manages CLI chat sessions
- Handles user input from terminal
- Publishes events to CLI channel
- Formats assistant responses for terminal output

**`QuartChatController`**
- Manages web chat sessions via Quart
- Handles HTTP requests and SSE streaming
- Publishes events to Quart channel
- Manages user sessions and thread persistence

### Core Handlers

**`RunThreadManager`**
- Manages OpenAI Assistant API threads and runs
- Handles message creation and retrieval
- Coordinates tool call execution
- Manages streaming responses

**Interface Contract:**
```python
- get_or_create_thread(assistant_id: str, user_id: Optional[str]) -> str  # Returns thread_id
- add_message_to_thread(thread_id: str, message: str, user_id: Optional[str]) -> str  # Returns message_id
- start_run(assistant_id: str, thread_id: str) -> Any  # Returns async stream of events
- submit_tool_outputs(thread_id: str, run_id: str, tool_outputs: Any) -> Any  # Submits tool results
```

**`ToolExecutor`**
- Executes tool calls from assistants
- Routes tool invocations to appropriate infrastructure
- Validates tool parameters
- Returns structured results
- **Note:** ToolExecutor is invoked by EventHandler when tool calls are required during `_handle_requires_action`.

**Interface Contract:**
```python
- execute(tool_name: str, **arguments: Any) -> Any  # Executes tool by name with arguments
- prepare_tool_output(tool_call: Any, result: Any, success: bool) -> Dict[str, Any]  # Formats output
```

**Note:** Tools are retrieved from `ToolsRegistry` via `agent_actions` dict passed to constructor.

**`EventHandler`**
- Coordinates event publishing
- Manages event routing to channels
- Handles event transformation
- Provides event filtering capabilities

**Interface Contract:**
```python
- start_run(assistant_id: str, thread_id: str, user_id: Optional[str]) -> None  # Starts assistant run
- _handle_message_delta(event_data: Any, thread_id: str) -> None  # Handles message deltas
- _handle_requires_action(run_data: Any, thread_id: str) -> None  # Handles tool calls
```

**`Channels` (BaseChannel interface)**
- Abstract base for all output channels
- Provides consistent interface for event publishing

**Interface Contract:**
```python
- publish_event(event: Any) -> None  # Publishes event to channel (abstract method)
```

**Note:** Channel activation is managed by `ChannelManager`, not individual channels.

### Configuration

**`flexiai/config/models.py`**
- Pydantic models for all environment variables
- Provider-specific settings (OpenAI, Azure, DeepSeek, Qwen, GitHub)
- General application settings
- Validation and type checking

**`flexiai/config/client_settings.py`**
- Aggregates all configuration models
- Provides unified configuration access
- Validates provider credentials

---

## Event-Oriented Execution Pipeline

FlexiAI Toolsmith uses an **event-oriented pipeline** (not a traditional event-driven architecture) for structured communication between components. This pipeline runs within a single process and does not require an external message broker.

### Event Flow

```
User Input
    ↓
Controller → Creates MessageEvent
    ↓
EventHandler → Routes events through internal dispatching (EventDispatcher / MultiChannelPublisher)
    ↓
RunThreadManager → Processes with Assistant API
    ↓
ToolExecutor → Executes tool calls (if needed, invoked by EventHandler)
    ↓
EventHandler → Publishes ResponseEvent to channels
    ↓
Channel → Streams to User (CLI/Web/Redis)
```

**Note:** EventBus exists as an internal utility, but primary event routing is handled by EventHandler and MultiChannelPublisher.

### Event Types

**Message Events**
- User messages
- Assistant responses
- Tool call requests
- Tool call results

**System Events**
- Thread creation
- Run status updates
- Error notifications
- Connection events

### Event Bus

The EventBus is an internal utility for component communication. Primary event routing is handled by:
- **EventHandler** - Orchestrates event processing and tool calls
- **EventDispatcher** - Routes events to appropriate handlers within EventHandler
- **MultiChannelPublisher** - Publishes events to configured output channels (CLI/Quart/Redis)

---

## Channel System

Channels are terminal consumers of events and do not participate in execution or routing logic. They serve as output mechanisms for assistant responses:

### CLI Channel (`cli_channel.py`)
- Terminal-based output
- Formatted text responses
- Interactive input handling
- Real-time streaming via terminal updates

### Quart Channel (`quart_channel.py`)
- Server-Sent Events (SSE) streaming
- WebSocket-like real-time updates
- HTTP request/response handling
- Session management

### Redis Channel (`redis_channel.py`)
- Pub/sub messaging
- Distributed communication
- Multi-instance coordination
- Event persistence (optional)

### Channel Manager (`channel_manager.py`)
- Dynamic channel activation based on `ACTIVE_CHANNELS`
- Channel lifecycle management
- Event routing to active channels
- Channel-specific configuration

---

## Provider Abstraction

FlexiAI Toolsmith supports multiple LLM providers through a unified interface.

**Provider Support & Code Paths:**
- Assistant API features (tool calls, streaming, threads) are gated by provider support
- Code paths branch in `flexiai/credentials/credentials.py` based on `CREDENTIAL_TYPE`
- OpenAI and Azure OpenAI: Full Assistant API support with `OpenAI-Beta: assistants=v2` header
- DeepSeek, Qwen, GitHub Azure Inference: Chat completions only, no Assistant API endpoints
- See `flexiai/credentials/credentials.py` for implementation details

### Credential Strategy Pattern

**`flexiai/credentials/credentials.py`**
- Strategy pattern for provider-specific client creation
- Validates provider credentials
- Creates appropriate client instances
- Handles provider-specific configuration

### Supported Providers

**OpenAI**
- Full Assistant API support
- Threads, runs, tool calls, streaming
- Organization and project support

**Azure OpenAI**
- Full Assistant API support
- Azure-specific endpoint configuration
- API version management

**DeepSeek / Qwen / GitHub Azure Inference**
- Chat completions only
- OpenAI SDK compatibility
- No Assistant API support

### Provider Selection

Providers are selected via `CREDENTIAL_TYPE` environment variable:
- `openai` → OpenAI client
- `azure` → Azure OpenAI client
- `deepseek` → DeepSeek client
- `qwen` → Qwen client
- `github_models` → GitHub Azure Inference client

---

## Tool Infrastructure

### Tools Registry (`tools_registry.py`)

Maps tool names to callable functions:
- Core tools (context storage, agent coordination)
- Infrastructure tools (CSV, spreadsheets)
- Business tools (subscriber management, security audit)
- Custom tools (user-defined)

### Tools Manager (`tools_manager.py`)

Implements core system operations:
- Context persistence (RAG)
- Agent coordination
- External API integration (YouTube)
- Tool dispatching

### Infrastructure Modules

**CSV Infrastructure**
- File operations
- Data validation
- Transformation utilities
- Query operations

**Spreadsheet Infrastructure**
- Excel/OpenPyXL operations
- Sheet management
- Formula execution
- Chart generation
- Data analysis

**Security Audit Infrastructure**
- Network reconnaissance
- Process detection
- Port scanning
- System updates
- Defense actions

See [TOOLING.md](TOOLING.md) for detailed tool documentation.

---

## Architecture Diagrams

### Message Workflow

<p align="center">
  <img src="../static/images/diagrams/FlexiAI%20Message%20Workflow-2026-01-22-113746.png" alt="FlexiAI Message Workflow Diagram: Shows complete message flow from user input through controllers, event handlers, assistant API processing, tool execution, and streaming responses back to users" style="max-width: 100%; height: auto;">
</p>

**Description:** End-to-end message workflow showing how user messages flow through the system from input (CLI or web) through controllers, event handlers, assistant API processing, optional tool execution, and real-time streaming responses back to users.

**Key Flow:**
1. User sends message via CLI or web interface
2. Controller (CLIChatController or QuartChatController) receives input
3. MessageEvent created and published to event system
4. RunThreadManager processes with Assistant API
5. EventHandler manages streaming events and tool calls
6. ToolExecutor handles tool calls (if required)
7. ResponseEvent published to channels (CLI/Quart/Redis)
8. Real-time streaming responses delivered to user

---

### Tool Execution Flow

<p align="center">
  <img src="../static/images/diagrams/FlexiAI%20Tool%20Execution%20Flow-2026-01-22-114151.png" alt="FlexiAI Tool Execution Flow Diagram: Shows tool call request from Assistant API through ToolExecutor, ToolsRegistry lookup, infrastructure module execution, and structured result return" style="max-width: 100%; height: auto;">
</p>

**Description:** Detailed workflow showing how tool calls are routed through the tool registry, executed by infrastructure modules, and returned to the assistant in a structured form.

**Key Flow:**
1. Assistant generates tool call request
2. ToolExecutor receives tool call
3. ToolsRegistry maps tool name to function
4. Infrastructure module executes operation
5. Structured result returned to ToolExecutor
6. Result formatted and sent to Assistant API
7. Assistant processes result and generates response

---

## Design Principles

### Modularity
- Clear separation between orchestration, tools, channels, and providers
- Pluggable tool architecture
- Independent channel implementations

### Extensibility
- Easy addition of new tools via registry
- Custom channel implementations
- Provider abstraction for new LLM services

### Maintainability
- Single responsibility per component
- Explicit interfaces between layers
- Comprehensive logging and error handling

### Performance
- Async/await throughout
- Streaming for real-time responses
- Efficient event routing

---

## Glossary

**Assistant API** – OpenAI's API for managing assistants, threads, runs, and tool calls. Provides structured interaction with LLM models.

**Run** – A single execution of an assistant on a thread. Contains messages, tool calls, and status.

**Thread** – A conversation context in the Assistant API. Contains messages and runs for a specific user.

**ToolCall** – A request from an assistant to execute a function. Contains tool name and parameters.

**MessageDeltaEvent** – An incremental update to a message as it's being generated. Used for streaming responses.

**SSE (Server-Sent Events)** – HTTP protocol for real-time streaming from server to client. Used for web interface.

---

## Related Documentation

- [WORKFLOW.md](WORKFLOW.md) – Detailed execution workflows
- [TOOLING.md](TOOLING.md) – Tool capabilities and usage
- [FILE_MAPPING.md](FILE_MAPPING.md) – Internal file reference
- [ENV_SETUP.md](ENV_SETUP.md) – Environment configuration
- [../SECURITY.md](../SECURITY.md) – Security guidelines