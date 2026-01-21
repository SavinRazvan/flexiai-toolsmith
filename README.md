# FlexiAI Toolsmith

**FlexiAI Toolsmith** is a modular Python framework for building applied AI assistants that combine large language models with structured context, backend tools, and external services.

The framework focuses on **orchestration, extensibility, and practical use cases**, enabling AI systems to move beyond generic chat and perform concrete tasks such as data processing, automation workflows, and system checks. It supports both CLI and web-based interaction with real-time streaming and a pluggable tool architecture.

FlexiAI Toolsmith was designed as a reusable foundation and has been used to build multiple applied systems, including:

* **Alina Assistant** – a customer service automation system handling identification, validation, and subscription workflows.
* **Security analysis agents** that perform structured configuration checks and inspections through controlled, tool-driven execution.

The project emphasizes clarity of architecture, modular design, and real-world usability rather than experimentation or model benchmarking.

---

## Key Characteristics

* **Modular Architecture** – Clear separation between orchestration, tools, channels, and providers.
* **Tool-Driven AI** – Assistants invoke structured tools via explicit tool calls instead of relying on free-form responses.
* **Context-Aware Workflows** – Structured context is injected into assistant interactions to ensure grounded behavior.
* **Multi-Channel Interaction** – CLI and web interfaces with real-time streaming via Server-Sent Events (SSE).
* **Event-Driven Design** – Pub/sub-style event flow for decoupled, maintainable components.
* **Provider Abstraction** – Unified interface for multiple LLM providers where supported.

---

## AI Provider Integration

FlexiAI Toolsmith supports multiple LLM providers through a unified interface.

Advanced Assistant API features (threads, runs, tool calls, streaming) are currently available for **OpenAI** and **Azure OpenAI**. Other providers are supported via chat-completions compatibility where applicable.

| Provider               | Assistant API | Chat Completions | Notes                          |
| ---------------------- | ------------- | ---------------- | ------------------------------ |
| OpenAI                 | ✅             | ✅                | Threads, streaming, tool calls |
| Azure OpenAI           | ✅             | ✅                | Threads, streaming, tool calls |
| DeepSeek               | ❌             | ✅                | OpenAI SDK compatible          |
| Qwen                   | ❌             | ✅                | OpenAI SDK compatible          |
| GitHub Azure Inference | ❌             | ✅                | Azure AI SDK                   |

---

## Context-Aware Tool Orchestration

FlexiAI Toolsmith enables assistants to combine model responses with structured context and deterministic tool execution.

Instead of relying on unconstrained generation, assistants:

* Build context from structured data sources
* Invoke explicit tools via tool calls
* Process results deterministically
* Feed validated outputs back into the assistant workflow

The framework also includes **experimental support for multi-agent coordination**, where assistants can share context and delegate tasks in a controlled manner.

---

## Architecture Diagrams

Visual overview of the FlexiAI Toolsmith architecture and workflows.

### 1. High-Level Architecture

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%201%20%E2%80%94%20High-Level%20Architecture-2026-01-21-201950.png" alt="High-Level Architecture Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** System architecture showing entry points, controllers, core handlers, event system, channels, and tool infrastructure. Illustrates how data flows through the framework.

---

### 2. Web Request Lifecycle

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%202%20%E2%80%94%20Web%20Request%20Lifecycle-2026-01-21-201839.png" alt="Web Request Lifecycle Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** End-to-end flow of a web request from browser interaction through Quart controllers, assistant execution, tool invocation (if required), and SSE streaming back to the client.

---

### 3. Tool Execution Flow

<p align="center">
  <img src="static/images/diagrams/DIAGRAM%203%20%E2%80%94%20Tool%20Execution%20Flow-2026-01-21-201759.png" alt="Tool Execution Flow Diagram" style="max-width: 100%; height: auto;">
</p>

**Description:** Workflow showing how tool calls are routed through the tool registry, executed by infrastructure modules, and returned to the assistant in a structured form.

---

## Built-in Tool Modules

### Core Capabilities

* **Context Storage** – Save and retrieve processed context across sessions.
* **Agent Coordination (Experimental)** – Controlled assistant communication and delegation.
* **Search Utilities** – External lookup helpers (e.g. YouTube search).
* **Product Filtering** – Structured data filtering utilities.

### Data Management

* **CSV Operations** – Create, read, update, validate, transform, and filter CSV data.
* **Spreadsheet Operations** – Excel/OpenPyXL-based tooling:

  * File and sheet management
  * Data entry and retrieval
  * Analysis, formulas, formatting
  * Validation, transformation, and chart generation

### Business-Oriented Tools

* **Subscriber Management** – Identification, billing lookup, and service handling workflows.
* **Security Analysis Tools** – Structured configuration checks and inspection routines executed through controlled workflows.

### Experimental

* **Dynamic Web Forms** – Generate interactive forms inside the web chat UI; submissions are persisted as structured data.
* **OCR Utilities** – Experimental OCR helpers (not yet integrated).

---

## Project Structure

```text
📦 flexiai-toolsmith
 ┣ 📂 flexiai
 ┃ ┣ 📂 agents              # Experimental multi-agent logic
 ┃ ┣ 📂 channels            # CLI, Quart SSE, Redis
 ┃ ┣ 📂 config              # Configuration & settings
 ┃ ┣ 📂 controllers         # CLI and web controllers
 ┃ ┣ 📂 core
 ┃ ┃ ┣ 📂 events            # Event models, bus, SSE manager
 ┃ ┃ ┗ 📂 handlers          # Thread manager, tool executor
 ┃ ┣ 📂 credentials         # Provider credentials
 ┃ ┣ 📂 database            # SQLAlchemy models (prepared)
 ┃ ┣ 📂 toolsmith           # Tool infrastructure
 ┃ ┗ 📂 utils               # Context utilities
 ┣ 📂 static                # Assets and diagrams
 ┣ 📂 templates             # Quart/Jinja templates
 ┣ 📂 logs                  # Application logs
 ┣ 📜 app.py                # Web entry point
 ┣ 📜 chat.py               # CLI entry point
 ┣ 📜 .env.template
 ┣ 📜 environment.yml
 ┣ 📜 requirements.txt
 ┣ 📜 Dockerfile
```

---

## Prerequisites

* Python 3.12+
* Conda or `pip` + `venv`
* Redis (optional, only if enabled)
* OpenAI or Azure OpenAI assistant ID

---

## Installation

```bash
git clone https://github.com/SavinRazvan/flexiai-toolsmith.git
cd flexiai-toolsmith
./setup_env.sh
```

Copy `.env.template` to `.env` and configure required variables.

---

## Usage

### CLI

```bash
python chat.py
```

### Web (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

Access:

* `http://127.0.0.1:8000/`
* `http://127.0.0.1:8000/chat/`

---

## Documentation

* `FILE_MAPPING.md` – Detailed file and dependency mapping
* `project_files_relations.md` – Workflow and execution paths
* `ENV_SETUP.md` – Environment configuration guide

---

## Contributing

Contributions are welcome. Please review the documentation before submitting changes and follow existing architectural patterns.

---

## License

Released under the **MIT License**.
