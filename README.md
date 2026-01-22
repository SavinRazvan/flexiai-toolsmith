# FlexiAI Toolsmith

[![Python >=3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
* **Event-Oriented Pipeline** – Structured event flow for streaming, tool calls, and output routing. Components publish/subscribe to internal events; not a full message-broker-based event-driven system.
* **Provider Abstraction** – Unified interface for multiple LLM providers where supported.

---

## AI Provider Integration

FlexiAI Toolsmith supports multiple LLM providers through a unified interface.

Advanced Assistant API features (threads, runs, tool calls, streaming) are currently available for **OpenAI** and **Azure OpenAI**. Assistant API support enables structured tool calls, streaming execution, and deterministic workflows. Other providers are supported via chat-completions compatibility where applicable.

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

## Architecture Overview

<p align="center">
  <img src="static/images/diagrams/FlexiAI%20Message%20Workflow-2026-01-22-113746.png" alt="FlexiAI Message Workflow Diagram" style="max-width: 100%; height: auto;">
</p>

**Message workflow** showing how user messages flow through controllers, event handlers, assistant API, and tool execution, with real-time streaming responses back to users via CLI or web interfaces.

For detailed architecture documentation, execution workflows, and additional diagrams, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/WORKFLOW.md](docs/WORKFLOW.md).

---

## Built-in Tooling

FlexiAI Toolsmith includes built-in tooling for:

* **Data Processing** – CSV and spreadsheet operations (Excel/OpenPyXL)
* **Business Workflows** – Subscriber management, customer service automation
* **Security Analysis** – Network reconnaissance, process detection, port scanning, system updates
* **External Integration** – YouTube search, external API helpers
* **Experimental** – Multi-agent coordination, dynamic web forms, OCR utilities

See [docs/TOOLING.md](docs/TOOLING.md) for complete tool documentation and capabilities.

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
* **Optional system dependencies:**
  * Tesseract OCR (for OCR features): `sudo apt-get install tesseract-ocr` (Linux) or `brew install tesseract` (macOS)
  * Redis (only if using Redis channel): `sudo apt-get install redis-server` (Linux) or `brew install redis` (macOS)
* OpenAI or Azure OpenAI assistant ID

---

## Installation

```bash
git clone https://github.com/SavinRazvan/flexiai-toolsmith.git
cd flexiai-toolsmith
./setup_env.sh
```

Copy `.env.template` to `.env` and configure required variables.

**Minimal `.env` example:**

```env
CREDENTIAL_TYPE=openai
OPENAI_API_KEY=sk-your-api-key-here
ASSISTANT_ID=your_assistant_id_here
USER_ID=default_user
ACTIVE_CHANNELS=cli,quart
```

> **Note:** See [docs/ENV_SETUP.md](docs/ENV_SETUP.md) for complete configuration options and provider-specific settings.

---

## Usage

### CLI

```bash
python chat.py
```

**Example CLI Interface:**

<p align="center">
  <img src="static/images/demos/Security%20Advisor%201%20(CLI%20Chat).png" alt="CLI Chat Example - Security Advisor" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
</p>

**Quick Test:**
```bash
python chat.py
# Expected output:
# ======================================
#          FlexiAI Chat Session         
# ======================================
# Type '/bye' or '/exit' to quit the conversation.
#
# 👤 You: hello
# 🌺 Assistant: Hello! How can I assist you today?
```

> **Troubleshooting:** If you see errors, verify `ASSISTANT_ID` and `OPENAI_API_KEY` are set correctly in your `.env` file.

### Web (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

Access:

* `http://127.0.0.1:8000/` - Landing page
* `http://127.0.0.1:8000/chat/` - Chat interface

**Example Web Interface:**

<p align="center">
  <img src="static/images/demos/FlexiAI%20-%20WebChat%20-%20Security%201.png" alt="Web Chat Example - Security Assistant" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
</p>

**Quick Test:**
1. Start the server: `hypercorn app:app --bind 127.0.0.1:8000 --workers 1`
2. Open `http://127.0.0.1:8000/chat/` in your browser
3. Send a message and observe real-time streaming responses (text should appear incrementally)

> **Troubleshooting:** If no streaming appears, verify `ASSISTANT_ID` and `OPENAI_API_KEY` are set correctly in your `.env` file.

---

## Documentation

* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) – System architecture, components, and design
* [docs/WORKFLOW.md](docs/WORKFLOW.md) – Execution workflows and data flow
* [docs/TOOLING.md](docs/TOOLING.md) – Tool capabilities and usage
* [docs/ENV_SETUP.md](docs/ENV_SETUP.md) – Environment configuration guide
* [SECURITY.md](SECURITY.md) – Security guidelines and safe usage practices
* [CONTRIBUTING.md](CONTRIBUTING.md) – Development guidelines and contribution process
* [TESTING.md](TESTING.md) – Testing guide and mocking strategies
* [docs/FILE_MAPPING.md](docs/FILE_MAPPING.md) – Internal file reference (for maintainers)

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code style, and submission process.

---

## License

Released under the **MIT License**.
