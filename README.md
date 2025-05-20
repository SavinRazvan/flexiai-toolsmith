# FlexiAI Toolsmith

**FlexiAI Toolsmith** is a flexible, multi-channel Python framework for building AI-powered chat assistants. It supports both CLI and web (Quart + SSE) interfaces, integrates with multiple AI providers via the OpenAI Python SDK, and enables assistants to invoke powerful tool plug-ins—including CSV/spreadsheet processing, YouTube search, security audits, dynamic forms, and (soon) OCR.

> **Provider Support Overview**
>
> * ✅ **OpenAI** and **Azure OpenAI** — full Assistant-API support
> * 🟡 **DeepSeek** and **Qwen** — use the OpenAI Python SDK but currently expose **only basic chat completions**
> * ❌ **GitHub Azure Inference** — limited to basic chat completions
>
> ⚙️ When Assistant-API support is added to any SDK-backed provider (e.g., DeepSeek or Qwen), FlexiAI Toolsmith will support it immediately with no code changes.


---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
   * [CLI Chat](#cli-chat-wsl)
   * [Web Chat (Quart + SSE)](#web-chat-quart--sse)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

### Multi-Channel Publishing

Chat events can be streamed to:

* **CLI** (`CLIChannel`)
* **Redis Pub/Sub** (`RedisChannel`)
* **SSE Web Clients** via Quart (`QuartChannel` + `SSEManager`)

### AI Provider Support

* **OpenAI & Azure OpenAI**: full Assistant-API support (threads, deltas, tool calls)
* **DeepSeek & Qwen**: basic chat completions via OpenAI SDK (Assistant-API pending provider-side)
* **GitHub Azure Inference**: basic chat completions only

### Streaming Assistant API

* Thread lifecycle management (create, queue, in-progress, complete)
* Event routing via an in-memory `EventBus` and `EventDispatcher`
* Delta-based message streaming using `MessageDeltaEvent`

### Dynamic RAG & Multi-Agent Tool Orchestration (via Toolsmith)

Toolsmith enables AI assistants to **invoke dynamic tools via tool calls**, forming a hybrid RAG + MAS system:

* **Agent Coordination & Delegation**
  * `save_processed_content` / `load_processed_content`
  * `initialize_agent` / `communicate_with_assistant`

This architecture supports agent-to-agent delegation, live retrieval from external systems, and operational workflows (beyond document search).

### Built-in Tool Plug-ins

* **YouTube Search**

  * `search_youtube` (opens browser)
  * `search_on_youtube` (returns embeddable HTML)
* **Product Filtering**

  * `filter_products` (registered as `ai_custom_products`)
* **CSV Operations**

  * `csv_operations` (CRUD via `csv_entrypoint`)
* **Subscriber Management**

  * `identify_subscriber`, `retrieve_billing_details`, `manage_services`
* **Spreadsheet Operations**

  * `file_operations`, `sheet_operations`
  * `data_entry_operations`, `data_retrieval_operations`
  * `data_analysis_operations`, `formula_operations`
  * `formatting_operations`, `data_validation_operations`
  * `data_transformation_operations`, `chart_operations`
* **Security Audits**

  * `security_audit` (recon, port scans, defenses, system updates)
* **Web Forms (Experimental)**

  * POST endpoint `/submit_user_info`, persists entries to CSV
* **OCR (Coming Soon)**

  * Placeholder at `flexiai/toolsmith/_recycle/OCR.py`

### Configurable & Extensible

* Pydantic-based `.env` configuration for credentials, channels, logging, etc.
* Modular factories for channels, credentials, event handlers, and tools
* Structured logging with rotating file and console support

---

## Architecture

```text
📦 flexiai-toolsmith
 ┣ 📂 flexiai
 ┃ ┣ 📂 channels
 ┃ ┣ 📂 config
 ┃ ┣ 📂 controllers
 ┃ ┣ 📂 core
 ┃ ┃ ┣ 📂 events
 ┃ ┃ ┗ 📂 handlers
 ┃ ┣ 📂 credentials
 ┃ ┣ 📂 database
 ┃ ┣ 📂 toolsmith
 ┃ ┗ 📂 utils
 ┣ 📂 static
 ┣ 📂 templates
 ┣ 📜 .env
 ┣ 📜 .env.template
 ┣ 📜 .gitignore
 ┣ 📜 app.py
 ┣ 📜 chat.py
 ┣ 📜 environment.yml
 ┣ 📜 requirements.in
 ┗ 📜 requirements.txt
```

---

## Prerequisites

* **Python 3.12+**
* **Redis** (required if using `redis` in `ACTIVE_CHANNELS`)
* **Conda** (Miniconda/Anaconda) *or* `pip` + `venv`

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/flexiai-toolsmith.git
   cd flexiai-toolsmith
   ```

2. **Set up the environment (Conda recommended):**

   ```bash
   conda env create -f environment.yml
   conda activate .conda_flexiai
   ```

   *Or set up a `venv` and install via pip:*

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Configuration

Copy `.env.template` to `.env`, then set:

| Variable                   | Description                                                          | Example           |
| -------------------------- | -------------------------------------------------------------------- | ----------------- |
| `CREDENTIAL_TYPE`          | AI provider (`openai`, `azure`, `deepseek`, `qwen`, `github_models`) | `openai`          |
| `OPENAI_API_KEY`, etc.     | Provider-specific credentials                                        | `sk-xxxx…`        |
| `ACTIVE_CHANNELS`          | Comma-separated list: `cli`, `redis`, `quart`                        | `cli`,`quart`,`cli,quart`       |
| `USER_PROJECT_ROOT_DIR`    | Absolute path to your project root                                   | `/home/user/code` |
| `YOUTUBE_API_KEY` *(opt.)* | Required for YouTube search integration                              | `AIza…`           |

> ℹ️ Full Assistant-API support currently applies to OpenAI and Azure OpenAI only.
> DeepSeek and Qwen will auto-enable when their endpoints support it.

---

## Usage

### CLI Chat (WSL or Linux)

```bash
python chat.py
```

* Prompts are prefixed as `👤 You`
* Assistant replies stream as `🌺 Assistant`

---

### Web Chat (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

1. Open your browser at [http://127.0.0.1:8000/chat/](http://127.0.0.1:8000/chat/)
2. Start chatting in the live SSE-powered UI

---

## Contributing

1. Fork the repo

2. Create a feature branch:

   ```bash
   git checkout -b feature/my-feature
   ```

3. Make changes with clear commit messages

4. Submit a pull request with context and purpose

---

## License

Licensed under the **MIT License**. See [LICENSE](LICENSE) for full terms.

