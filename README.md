# FlexiAI Toolsmith

> **Build production-ready AI assistants with multi-channel support, dynamic tool orchestration, and seamless provider integration.**

**FlexiAI Toolsmith** is a flexible, enterprise-grade Python framework for building AI-powered chat assistants. It provides a unified interface for multiple AI providers, supports both CLI and web interfaces with real-time streaming, and enables assistants to invoke powerful tool plug-ins through a dynamic orchestration system.

## 🚀 Key Features

* **Multi-Channel Architecture** — Deploy to CLI, web (Quart + SSE), or Redis Pub/Sub simultaneously
* **Multi-Provider Support** — Seamlessly switch between OpenAI, Azure OpenAI, DeepSeek, Qwen, and GitHub Azure Inference
* **Dynamic Tool System** — Extensible tool registry with built-in support for CSV/spreadsheet operations, YouTube search, security audits, dynamic forms, and more
* **Event-Driven Design** — Pub/sub event bus for decoupled, scalable communication
* **Production Ready** — Structured logging, error handling, session management, and Docker support

## 🤖 AI Provider Support

| Provider | Assistant API | Chat Completions | Notes |
|----------|---------------|------------------|-------|
| **OpenAI** | ✅ Full Support | ✅ | Threads, deltas, tool calls, streaming |
| **Azure OpenAI** | ✅ Full Support | ✅ | Threads, deltas, tool calls, streaming |
| **DeepSeek** | ❌ Not Supported | ✅ | OpenAI SDK compatible, chat completions only |
| **Qwen** | ❌ Not Supported | ✅ | OpenAI SDK compatible, chat completions only |
| **GitHub Azure Inference** | ❌ Not Supported | ✅ | Azure AI SDK, chat completions only |

> **Note:** Assistant API (threads, runs, tool calls) is currently only available for OpenAI and Azure OpenAI. DeepSeek and Qwen use OpenAI SDK compatibility for chat completions, but do not support Assistant API endpoints. If these providers add Assistant API support in the future, code changes would be required to add the appropriate headers and configuration.

---

## Table of Contents

1. [Key Features](#-key-features)  
2. [AI Provider Support](#-ai-provider-support)  
3. [Detailed Features](#detailed-features)  
4. [Architecture Diagrams](#architecture-diagrams)  
5. [Architecture](#architecture)  
6. [Prerequisites](#prerequisites)  
7. [Installation](#installation)  
8. [Configuration](#configuration)  
9. [Usage](#usage)  
   * [CLI Chat](#cli-chat)  
   * [Web Chat (Quart + SSE)](#web-chat-quart--sse)  
10. [Running with Docker](#running-with-docker)  
11. [Documentation](#documentation)  
12. [Contributing](#contributing)  
13. [License](#license)

---

## Detailed Features

### Multi-Channel Publishing

Chat events can be streamed to multiple channels simultaneously:

* **CLI** (`CLIChannel`) — Interactive terminal interface with real-time streaming
* **Redis Pub/Sub** (`RedisChannel`) — Distributed messaging for microservices
* **SSE Web clients** via Quart (`QuartChannel` + `SSEManager`) — Real-time browser updates

### Streaming Assistant API

* Thread life-cycle management (create → queue → in-progress → complete)  
* Event routing via in-memory `EventBus` + `EventDispatcher`  
* Delta-based message streaming with `MessageDeltaEvent`

### Dynamic RAG & Multi-Agent Tool Orchestration

Toolsmith enables assistants to **invoke dynamic tools via tool calls**, providing a hybrid RAG + Multi-Agent System:

* **Agent coordination & delegation**  
  * `save_processed_content` / `load_processed_content`  
  * `initialize_agent` / `communicate_with_assistant`

---

## Architecture Diagrams

Visual overview of the FlexiAI Toolsmith architecture and workflows:

### 1. High-Level Architecture

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%201%20%E2%80%94%20High-Level%20Architecture-2026-01-21-201950.png" alt="High-Level Architecture Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** Complete system architecture showing entry points (`app.py`, `chat.py`), controllers, core handlers, event system, channels, and tool infrastructure. Illustrates how components interact and data flows through the system.

---

### 2. Web Request Lifecycle

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%202%20%E2%80%94%20Web%20Request%20Lifecycle-2026-01-21-201839.png" alt="Web Request Lifecycle Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** End-to-end flow of a web request from browser HTTP POST through Quart controller, OpenAI Assistant API, event processing, tool execution (if needed), and SSE streaming back to the browser. Shows the complete request/response cycle.

---

### 3. Tool Execution Flow

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%203%20%E2%80%94%20Tool%20Execution%20Flow-2026-01-21-201759.png" alt="Tool Execution Flow Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** Detailed workflow of tool execution from AI assistant tool call request through tool registry lookup, tool manager execution, infrastructure modules (CSV/Spreadsheet/Security), result processing, and submission back to the assistant.

---

> **📖 For detailed file relationships and workflows, see:**
> - [`FILE_MAPPING.md`](FILE_MAPPING.md) - Complete file mapping with detailed imports/exports and relationships
> - [`project_files_relations.md`](project_files_relations.md) - Complete workflow documentation

## Built-in Tool Plug-ins

### Core Tools
* **RAG (Retrieval-Augmented Generation)** — `save_processed_content`, `load_processed_content`  
* **Multi-Agent Coordination** — `initialize_agent`, `communicate_with_assistant`  
* **YouTube Search** — `search_youtube`, `search_on_youtube` (requires `YOUTUBE_API_KEY`)  
* **Product Filtering** — `filter_products` (`ai_custom_products`)  

### Data Management
* **CSV Operations** — `csv_operations` (full CRUD: create, read, update, delete, filter, validate, transform)  
* **Spreadsheet Operations** — Complete Excel/OpenPyXL support:
  - `file_operations` - Create, open, close spreadsheets
  - `sheet_operations` - Sheet management
  - `data_entry_operations` - Write data to cells
  - `data_retrieval_operations` - Read data from cells
  - `data_analysis_operations` - Analyze spreadsheet data
  - `formula_operations` - Formula management
  - `formatting_operations` - Cell formatting
  - `data_validation_operations` - Data validation
  - `data_transformation_operations` - Data transformation
  - `chart_operations` - Chart creation

### Business Tools
* **Subscriber Management** — `identify_subscriber`, `retrieve_billing_details`, `manage_services`  
* **Security Audits** — `security_audit` (reconnaissance, port scans, defenses, updates)  

### Experimental
* **Web Forms** — Generates interactive forms as Markdown in the Quart/SSE chat UI; submissions are sent via POST to `/submit_user_info` and persisted to CSV
* **OCR** — `flexiai/toolsmith/_recycle/ocr_utils.py` (Coming Soon - experimental, not yet integrated)

## Configurable & Extensible

* **Pydantic-based Configuration** — Type-safe `.env` configuration with validation
* **Modular Architecture** — Factory patterns for channels, credentials, handlers, tools
* **Structured Logging** — Rotating file logs + console output with configurable levels
* **Multi-Provider Support** — Unified interface for multiple AI providers
* **Event-Driven Design** — Pub/sub event bus for decoupled communication
* **Tool Registry System** — Dynamic tool registration and execution
* **Database Support** — SQLAlchemy ORM (prepared for future features)
* **Experimental Agents** — Multi-agent system framework (in `flexiai/agents/`)

---

## Architecture

### Project Structure

```text
📦 flexiai-toolsmith
 ┣ 📂 flexiai
 ┃ ┣ 📂 agents              # Multi-agent system (experimental)
 ┃ ┣ 📂 channels            # Event publishing (CLI, Quart SSE, Redis)
 ┃ ┣ 📂 config              # Configuration & settings management
 ┃ ┣ 📂 controllers         # Application controllers (CLI & Web)
 ┃ ┣ 📂 core
 ┃ ┃ ┣ 📂 events            # Event models, bus, SSE manager
 ┃ ┃ ┗ 📂 handlers          # Event handler, thread manager, tool executor
 ┃ ┣ 📂 credentials         # AI provider credential management
 ┃ ┣ 📂 database            # Database models & connection (SQLAlchemy)
 ┃ ┣ 📂 toolsmith           # Tool infrastructure (CSV, Spreadsheet, Security)
 ┃ ┗ 📂 utils               # Utility functions (context management)
 ┣ 📂 static                # CSS, JavaScript, images
 ┣ 📂 templates             # HTML templates (Quart/Jinja2)
 ┣ 📂 logs                  # Application logs
 ┣ 📜 app.py                # Web entry point (Quart server)
 ┣ 📜 chat.py               # CLI entry point
 ┣ 📜 .env                  # Environment variables (git-ignored)
 ┣ 📜 .env.template         # Environment template
 ┣ 📜 environment.yml       # Conda environment
 ┣ 📜 requirements.txt      # Python dependencies
 ┣ 📜 requirements.in      # Source dependencies
 ┣ 📜 setup_env.sh         # Automated setup script
 ┗ 📜 Dockerfile            # Docker configuration
```

### Core Components

**Entry Points:**
- `app.py` - Web application (Quart + SSE)
- `chat.py` - CLI application

**Configuration Chain:**
- `config/models.py` → `config/client_settings.py` → `credentials/credentials.py` → `config/client_factory.py`

**Event Flow:**
- Controllers → Event Handler → Event Dispatcher → Tool Executor → Tools Registry → Tools Manager

**Channel System:**
- Multi-Channel Publisher → Channel Manager → Individual Channels (CLI/Quart/Redis) → Event Bus

**Tool System:**
- Tools Manager → Tools Registry → Infrastructure Modules (CSV/Spreadsheet/Security)

For detailed file relationships and workflows, see:
- [`FILE_MAPPING.md`](FILE_MAPPING.md) - Complete file mapping with detailed imports/exports and relationships
- [`project_files_relations.md`](project_files_relations.md) - Complete workflow and relations

---

## Prerequisites

* **Python 3.12+** (Python 3.13 also supported)
* **Conda** (Miniconda/Anaconda) *or* `pip` + `venv`
* **Redis** (optional - only needed if `redis` is in `ACTIVE_CHANNELS`)
* **OpenAI Assistant** - Create an assistant in OpenAI/Azure dashboard and get the `ASSISTANT_ID`

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/SavinRazvan/flexiai-toolsmith.git
   cd flexiai-toolsmith
   ```

2. **Set up the environment**

   **Option A: Automated Setup (Recommended)**
   ```bash
   ./setup_env.sh
   ```
   The script will guide you through Conda or venv setup and create your `.env` file.

   **Option B: Manual Setup with Conda**
   ```bash
   conda env create -f environment.yml
   conda activate .conda_flexiai
   cp .env.template .env
   # Edit .env with your settings
   ```

   **Option C: Manual Setup with venv**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Configure your environment**

   Edit `.env` and set at minimum:
   - `CREDENTIAL_TYPE` - Your AI provider
   - `ASSISTANT_ID` - Your assistant ID (get from OpenAI/Azure dashboard)
   - `USER_ID` - User identifier
   - Provider-specific API keys

   See [Configuration](#configuration) section for all options.

---

## Configuration

### Required Setup

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` with your settings:**

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CREDENTIAL_TYPE` | AI provider: `openai`, `azure`, `deepseek`, `qwen`, `github_models` | `openai` |
| `ASSISTANT_ID` | **Required** - Your OpenAI/Azure Assistant ID | `asst_abc123...` |
| `USER_ID` | **Required** - User identifier for sessions | `user_123` |

#### Provider-Specific Credentials

**For OpenAI:**
- `OPENAI_API_KEY` - Your OpenAI API key

**For Azure OpenAI:**
- `AZURE_OPENAI_API_KEY` - Azure API key
- `AZURE_OPENAI_ENDPOINT` - Azure endpoint URL

**For DeepSeek:**
- `DEEPSEEK_API_KEY` - DeepSeek API key

**For Qwen:**
- `QWEN_API_KEY` - Qwen API key

**For GitHub Azure Inference:**
- `GITHUB_TOKEN` - GitHub personal access token

#### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ACTIVE_CHANNELS` | Channels to use: `cli`, `redis`, `quart` (comma-separated) | `cli` |
| `USER_PROJECT_ROOT_DIR` | Absolute path for project files | Empty |
| `ASSISTANT_NAME` | Display name for assistant | `Assistant` |
| `USER_NAME` | Display name for user | `User` |
| `SECRET_KEY` | Secret key for Quart sessions | `fallback-secret` |
| `YOUTUBE_API_KEY` | Needed for YouTube search tool | None |
| `DATABASE_URL` | Database connection string (SQLite default) | Auto-generated |
| `REDIS_URL` | Redis connection URL (if using Redis channel) | `redis://localhost:6379/0` |

> **Note:** Assistant-API features (threads, runs, tool calls, streaming) currently work on OpenAI & Azure OpenAI only. DeepSeek and Qwen support chat completions via OpenAI SDK compatibility, but do not support Assistant API endpoints.

> **Tip:** See [`ENV_SETUP.md`](ENV_SETUP.md) for detailed setup instructions.

---

## Usage

### CLI Chat

```bash
# Activate environment first
conda activate .conda_flexiai  # or: source .venv/bin/activate

# Run CLI chat
python chat.py
```

**Features:**
* Prompts show as `👤 You`
* Assistant messages stream as `🌺 Assistant`
* Real-time streaming responses
* Tool execution with progress indicators
* Works on Linux, macOS, and WSL

### Web Chat (Quart + SSE)

```bash
# Activate environment first
conda activate .conda_flexiai  # or: source .venv/bin/activate

# Run web server
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

**Access:**
1. Browse to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** (landing page)
2. Navigate to **[http://127.0.0.1:8000/chat/](http://127.0.0.1:8000/chat/)** (chat interface)
3. Start chatting in the live SSE UI

**Features:**
* Server-Sent Events (SSE) for real-time streaming
* Interactive web interface
* Form generation and submission
* Session management
* Multi-user support

---

## Running with Docker

You can run FlexiAI Toolsmith in a container without installing Python or dependencies on your host.

### 1. Build the Docker image

```bash
docker build -t flexiai-toolsmith .
```

### 2. Run the container

```bash
docker run -p 8000:8000 flexiai-toolsmith
```

The web interface will be available at [http://localhost:8000/chat/](http://localhost:8000/chat/).

> **Note:**  
> Make sure your `.env` file is present in the project root before building the image.  
> For production, consider using `hypercorn` as the entrypoint.

---

## Documentation

Comprehensive documentation is available:

* **[`FILE_MAPPING.md`](FILE_MAPPING.md)** - Complete file mapping with detailed imports/exports, relationships, and module overview
* **[`project_files_relations.md`](project_files_relations.md)** - Complete project workflow and file relations
* **[`ENV_SETUP.md`](ENV_SETUP.md)** - Detailed environment setup guide

## Project Statistics

* **Total Python Files**: 113
* **Core Application**: ~30 files
* **Tool Infrastructure**: ~50 files
* **Agents (Experimental)**: ~30 files
* **Configuration**: 4 files
* **Controllers**: 2 files (CLI & Web)
* **Channels**: 6 files (CLI, Quart SSE, Redis)
* **Core Handlers**: 5 files
* **Core Events**: 5 files

## Contributing

1. **Fork** ➜ create a feature branch

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Review the documentation**
   - Read [`FILE_MAPPING.md`](FILE_MAPPING.md) to understand the architecture
   - Check [`project_files_relations.md`](project_files_relations.md) for workflow details

3. **Follow the code structure**
   - Use existing patterns (factories, registries, channels)
   - Add tools via the ToolsRegistry system
   - Follow the event-driven architecture

4. **Commit with clear messages**

5. **Open a pull request** explaining context & purpose

---

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE) for full terms.

