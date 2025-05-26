# FlexiAI Toolsmith

**FlexiAI Toolsmith** is a flexible, multi-channel Python framework for building AI-powered chat assistants. It supports both CLI and web (Quart + SSE) interfaces, integrates with multiple AI providers via the OpenAI Python SDK, and enables assistants to invoke powerful tool plug-ins—including CSV / spreadsheet processing, YouTube search, security audits, dynamic forms, and (soon) OCR.

> **Provider Support Overview**
>
> * ✅ **OpenAI** and **Azure OpenAI** — full Assistant-API support  
> * 🟡 **DeepSeek** and **Qwen** — OpenAI SDK, but **chat-completions only** for now  
> * ❌ **GitHub Azure Inference** — chat-completions only  
>
> ⚙️ When any SDK-backed provider adds Assistant-API support, FlexiAI Toolsmith will pick it up automatically—no code changes required.

---

## Table of Contents

1. [Features](#features)  
2. [Tutorials / Quick Demos](#tutorials--quick-demos)  
3. [Architecture](#architecture)  
4. [Prerequisites](#prerequisites)  
5. [Installation](#installation)  
6. [Configuration](#configuration)  
7. [Usage](#usage)  
   * [CLI Chat (WSL or Linux)](#cli-chat-wsl-or-linux)  
   * [Web Chat (Quart -- SSE)](#web-chat-quart--sse)  
8. [Contributing](#contributing)  
9. [License](#license)

---

## Features

### Multi-Channel Publishing

Chat events can be streamed to:

* **CLI** (`CLIChannel`)  
* **Redis Pub/Sub** (`RedisChannel`)  
* **SSE Web clients** via Quart (`QuartChannel` + `SSEManager`)

---

## Tutorials / Quick Demos


<p align="center">
  <a href="https://youtu.be/XbPTmP0oD44" target="_blank">
    <img src="https://img.youtube.com/vi/XbPTmP0oD44/0.jpg" alt="▶ Quick Test: Quart channel demo" width="360">
  </a>
  &nbsp;&nbsp;
  <a href="https://youtu.be/HYyQQHaRzZ0" target="_blank">
    <img src="https://img.youtube.com/vi/HYyQQHaRzZ0/0.jpg" alt="▶ Quick Test: CLI channel demo" width="360">
  </a>
</p>

---

## AI Provider Support

* **OpenAI & Azure OpenAI** — full Assistant-API (threads, deltas, tool calls)  
* **DeepSeek & Qwen** — chat-completions via OpenAI SDK (Assistant-API pending)  
* **GitHub Azure Inference** — chat-completions only  

## Streaming Assistant API

* Thread life-cycle management (create → queue → in-progress → complete)  
* Event routing via in-memory `EventBus` + `EventDispatcher`  
* Delta-based message streaming with `MessageDeltaEvent`

## Dynamic RAG & Multi-Agent Tool Orchestration (via Toolsmith)

Toolsmith lets assistants **invoke dynamic tools via tool calls**, giving you a hybrid RAG + MAS system:

* **Agent coordination & delegation**  
  * `save_processed_content` / `load_processed_content`  
  * `initialize_agent` / `communicate_with_assistant`

## Built-in Tool Plug-ins

* **YouTube Search** — `search_youtube`, `search_on_youtube`  
* **Product Filtering** — `filter_products` (`ai_custom_products`)  
* **CSV Operations** — `csv_operations` (CRUD)  
* **Subscriber Management** — `identify_subscriber`, `retrieve_billing_details`, `manage_services`  
* **Spreadsheet Operations** — `file_operations`, `sheet_operations`, `data_entry_operations`, …  
* **Security Audits** — `security_audit` (recon, port scans, defenses, updates)  
* **Web Forms (Experimental)** — Generates interactive forms as Markdown in the Quart/SSE chat UI; submissions are sent via a POST to `/submit_user_info` and persisted to CSV
* **OCR (Coming Soon)** — `flexiai/toolsmith/_recycle/OCR.py`

## Configurable & Extensible

* Pydantic-based `.env` for credentials, channels, logging, …  
* Modular factories for channels, credentials, handlers, tools  
* Structured logging with rotating file + console outputs

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
* **Redis** (if `redis` in `ACTIVE_CHANNELS`)
* **Conda** (Miniconda/Anaconda) *or* `pip` + `venv`

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/SavinRazvan/flexiai-toolsmith.git
   ```

2. **Set up the environment (Conda recommended)**

   ```bash
   conda env create -f environment.yml
   conda activate .conda_flexiai
   ```

   *Or use `venv` + `pip`:*

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Configuration

Copy `.env.template` ➜ `.env`, then edit:

| Variable                 | Description                                            | Example           |
| ------------------------ | ------------------------------------------------------ | ----------------- |
| `CREDENTIAL_TYPE`        | `openai`, `azure`, `deepseek`, `qwen`, `github_models` | `openai`          |
| `OPENAI_API_KEY`, …      | Provider credentials                                   | `sk-…`            |
| `ACTIVE_CHANNELS`        | `cli`, `redis`, `quart` (comma-separated)              | `cli,quart`       |
| `USER_PROJECT_ROOT_DIR`  | Absolute project root path                             | `/home/user/code` |
| `YOUTUBE_API_KEY` (opt.) | Needed for YouTube search tool                         | `AIza…`           |

> ℹ️ Assistant-API features currently work on OpenAI & Azure OpenAI only; DeepSeek & Qwen auto-enable once their endpoints support it.

---

## Usage

### CLI Chat (WSL or Linux)

```bash
python chat.py
```

* Prompts show as `👤 You`
* Assistant messages stream as `🌺 Assistant`

### Web Chat (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

1. Browse to **[http://127.0.0.1:8000/chat/](http://127.0.0.1:8000/chat/)**
2. Start chatting in the live SSE UI

---

## Contributing

1. **Fork** ➜ create a feature branch

   ```bash
   git checkout -b feature/my-feature
   ```

2. Commit with clear messages

3. Open a **pull request** explaining context & purpose

---

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE) for full terms.

