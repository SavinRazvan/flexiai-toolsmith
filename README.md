# FlexiAI Toolsmith

**FlexiAI Toolsmith** is a flexible, multi-channel framework for building AI-powered chat assistants. It supports both CLI and web (Quart + SSE) interfaces, integrates with multiple AI providers (OpenAI, Azure OpenAI, DeepSeek, Qwen, GitHub Azure Inference), and lets you wire in rich “tools” (CSV/spreadsheets, security audits, YouTube embeds, web forms—and soon OCR).


> **Note:**
>
> * **OpenAI** and **Azure OpenAI** already provide the full Assistant-API (threads, streaming deltas, tool calls).
> * **DeepSeek** and **Qwen** currently use the OpenAI-compatible chat SDK for basic completions; once they expose the Assistant-API through that SDK, FlexiAI Toolsmith will immediately support their threads, streaming deltas, and tool calls too.
> * **GitHub Azure Inference** remains limited to basic chat completions.


---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
    1. [CLI Chat (WSL)](#cli-chat-wsl)
    2. [Web Chat (Quart + SSE)](#web-chat-quart--sse)
    3. [Submitting User Info (Web Forms)](#submitting-user-info-web-forms)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

- **Multi-Channel Publishing**  
  Fan-out chat events to:
  - **CLI** (`CLIChannel`)  
  - **Redis Pub/Sub** (`RedisChannel`)  
  - **SSE web clients** via Quart (`QuartChannel` + `SSEManager`)

- **AI Provider Support**  
  - **OpenAI & Azure OpenAI**: full Assistant-API (threads, streaming deltas, tool calls)  
  - **DeepSeek & Qwen**: OpenAI-compatible basic chat (Assistant-API planned)  
  - **GitHub Azure Inference**: basic chat completions only

- **Streaming Assistant API**  
  - Thread lifecycle management (create, queue, in-progress, complete)  
  - Run & message events routed through an in-memory `EventBus` and `EventDispatcher`  
  - Partial “delta” message streaming via `MessageDeltaEvent`

- **Pluggable Tool Suite**  
  - **Retrieval-Augmented Generation (RAG)**  
    - `save_processed_content` / `load_processed_content`  
  - **Assistant Orchestration**  
    - `initialize_agent` / `communicate_with_assistant`  
  - **YouTube Search**  
    - `search_youtube` (opens browser)  
    - `search_on_youtube` (embeddable HTML snippets)  
  - **Product Filtering**  
    - `filter_products` (registered as `ai_custom_products`)  
  - **CSV Operations**  
    - `csv_operations` (CRUD via `csv_entrypoint`)  
  - **Subscriber Management**  
    - `identify_subscriber`, `retrieve_billing_details`, `manage_services`  
  - **Spreadsheet Operations**  
    - `file_operations`, `sheet_operations`  
    - `data_entry_operations`, `data_retrieval_operations`  
    - `data_analysis_operations`, `formula_operations`  
    - `formatting_operations`, `data_validation_operations`  
    - `data_transformation_operations`, `chart_operations`  
  - **Security Audits**  
    - `security_audit` (reconnaissance, process listing, port/network scan, defense actions, system updates)  
  - **Web Forms** (Experimental)
    - `/submit_user_info` endpoint, persisting submissions to CSV  
  - **OCR (coming soon)**  
    - Placeholder at `flexiai/toolsmith/_recycle/OCR.py`

- **Configurable & Extensible**  
  - Pydantic-backed `.env` settings for channels, credentials, logging, etc.  
  - Modular factories for channels, credentials, event handlers, and tools  
  - Structured logging with rotating file and console handlers  

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
 ┣ 📜 .env.template
 ┣ 📜 .gitignore
 ┣ 📜 app.py
 ┣ 📜 chat.py
 ┣ 📜 environment_full.yml
 ┣ 📜 requirements.in
 ┗ 📜 requirements.txt
```

---

## Prerequisites

* **Python 3.13+**
* **Redis** (if you enable `redis` in `ACTIVE_CHANNELS`)
* **Conda** (Miniconda/Anaconda) *or* **pip** for dependency management

---

## Installation

1. **Clone** the repository:

   ```bash
   git clone https://github.com/your-username/flexiai-toolsmith.git
   cd flexiai-toolsmith
   ```

2. **Create** the Conda environment (recommended):

   ```bash
   conda env create -f environment_full.yml
   conda activate .conda_flexiai
   ```

   *or*, install via **pip** in a venv:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Configuration

Copy `.env.template` to `.env` and set:

| Variable                       | Description                                                          | Example           |
| ------------------------------ | -------------------------------------------------------------------- | ----------------- |
| **CREDENTIAL\_TYPE**           | AI provider (`openai`, `azure`, `deepseek`, `qwen`, `github_models`) | `openai`          |
| **OPENAI\_API\_KEY**, etc.     | Credentials for the selected provider                                | `sk-xxxx…`        |
| **ACTIVE\_CHANNELS**           | Comma-separated list (`cli`, `redis`, `quart`)                       | `cli`,`quart`,`cli,quart`|
| **USER\_PROJECT\_ROOT\_DIR**   | Absolute path to your project                                        | `/home/user/code` |
| **YOUTUBE\_API\_KEY** *(opt.)* | Required for `search_on_youtube`                                     | `AIza…`           |

> Only `openai` and `azure` support Assistant-API features—others use basic chat for now.

---

## Usage

### CLI Chat (WSL)

```bash
python chat.py
```

* Persists or generates `~/.flexiai_user_id`
* Prompts as **👤 You**, streams replies as **🌺 Artemis**

### Web Chat (Quart + SSE)

```bash
hypercorn app:app --bind 127.0.0.1:8000 --workers 1
```

1. Browse to `http://127.0.0.1:8000/chat/`
2. Interact via the SSE-powered chat UI

### Experimental: Dynamic Form Rendering & Submission in Chat

The built-in form POSTs to `/submit_user_info` and appends entries to:

```
flexiai/toolsmith/data/csv/user_submissions.csv
```

---

## Contributing

1. Fork the repo
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```
3. Implement & document your changes
4. Submit a Pull Request


---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
