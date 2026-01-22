# FlexiAI Toolsmith - Tool Infrastructure

This document describes the built-in tool modules, their capabilities, and usage patterns.

---

## Table of Contents

1. [Tool Architecture](#tool-architecture)
2. [Core Capabilities](#core-capabilities)
3. [Data Management Tools](#data-management-tools)
4. [Business-Oriented Tools](#business-oriented-tools)
5. [Security Analysis Tools](#security-analysis-tools)
6. [Experimental Tools](#experimental-tools)
7. [Tool Registration](#tool-registration)

---

## Tool Architecture

Tools in FlexiAI Toolsmith follow a consistent pattern:

1. **Tool Registry** (`tools_registry.py`) - Maps tool names to callable functions
2. **Tools Manager** (`tools_manager.py`) - Implements core tool operations
3. **Infrastructure Modules** - Specialized tool implementations (CSV, spreadsheets, security)

### Tool Execution Flow

```
Assistant Tool Call Request
  ↓
ToolCallExecutor
  ↓
ToolsRegistry (name → function mapping)
  ↓
ToolsManager or Infrastructure Module
  ↓
Structured Result
  ↓
Back to Assistant
```

---

## Core Capabilities

### Context Storage

**Tools:**
- `save_processed_content` - Save processed context for retrieval
- `load_processed_content` - Load previously saved context

**Purpose:** Enables retrieval-augmented generation (RAG) by persisting processed content across sessions.

**Use Cases:**
- Storing analysis results for later reference
- Maintaining conversation context
- Building knowledge bases from interactions

### Agent Coordination (Experimental)

**Tools:**
- `initialize_agent` - Initialize a new assistant agent
- `communicate_with_assistant` - Send messages between assistants

**Purpose:** Enables multi-agent coordination where assistants can delegate tasks and share context.

**Status:** Experimental - not fully integrated into main workflows.

### Search Utilities

**Tools:**
- `search_youtube` - Search YouTube videos
- `search_on_youtube` - Alternative YouTube search interface

**Purpose:** External lookup helpers for retrieving information from YouTube.

**Requirements:** `YOUTUBE_API_KEY` environment variable.

---

## Data Management Tools

### CSV Operations

**Tool:** `csv_operations`

**Capabilities:**
- **File Operations** - Create, read, update, delete CSV files
- **Data Entry** - Add single rows or bulk data
- **Data Retrieval** - Query and filter CSV data
- **Data Validation** - Validate data types and constraints
- **Data Transformation** - Transform and reshape data
- **Query Operations** - Filter, sort, and aggregate data

**Infrastructure:**
- Entry point: `csv_entrypoint.py`
- Manager: `csv_manager.py`
- Operations: Modular operation handlers
- Utilities: Error handling, validation helpers

**Example Operations:**
- `create` - Create new CSV file
- `read` - Read CSV data
- `add_row` - Add single row
- `add_rows` - Add multiple rows
- `filter` - Filter rows by condition
- `update` - Update specific cells
- `validate` - Validate data integrity

**Example Usage:**

```python
# Create CSV file
csv_entrypoint(
    operation="create",
    path="data",
    file_name="users.csv",
    rows=[{"name": "Alice", "email": "alice@example.com"}]
)

# Read CSV data
csv_entrypoint(
    operation="read",
    path="data",
    file_name="users.csv"
)

# Filter rows
csv_entrypoint(
    operation="filter_rows",
    path="data",
    file_name="users.csv",
    condition_type="equals",
    column="name",
    condition_value="Alice"
)

# Add row (append_row operation)
csv_entrypoint(
    operation="append_row",
    path="data",
    file_name="users.csv",
    row={"name": "Bob", "email": "bob@example.com"}
)
```

**Note:** Tools are called via the tool registry, which routes to `csv_entrypoint()` function.

**Rate Limits & Timeouts:**
- File operations: No timeout (immediate)
- Large files (>10MB): Consider chunking for better performance
- Default timeout: None (operations complete synchronously)

### Spreadsheet Operations

**Tool:** Multiple specialized tools for Excel/OpenPyXL operations

**Tools:**
- `file_operations` - File and workbook management
- `sheet_operations` - Sheet creation, deletion, management
- `data_entry_operations` - Cell and range data entry
- `data_retrieval_operations` - Read data from sheets
- `data_analysis_operations` - Statistical analysis
- `formula_operations` - Excel formula execution
- `formatting_operations` - Cell and range formatting
- `data_validation_operations` - Data validation rules
- `data_transformation_operations` - Data reshaping
- `chart_operations` - Chart creation and management

**Infrastructure:**
- Entry point: `spreadsheet_entrypoint.py`
- Manager: `spreadsheet_manager.py`
- Operations: Specialized operation modules
- Utilities: Mixed helpers, error handling

**Capabilities:**
- **File Management** - Create, open, save Excel files
- **Sheet Management** - Create, delete, rename sheets
- **Data Entry** - Write data to cells and ranges
- **Data Retrieval** - Read data with filtering and sorting
- **Analysis** - Statistical functions and aggregations
- **Formulas** - Excel formula support
- **Formatting** - Cell styles, colors, fonts
- **Validation** - Data validation rules
- **Transformation** - Pivot tables, data reshaping
- **Charts** - Create and modify charts

---

## Business-Oriented Tools

### Subscriber Management

**Tools:**
- `identify_subscriber` - Identify subscriber from data
- `retrieve_billing_details` - Get billing information
- `manage_services` - Manage subscriber services

**Purpose:** Customer service automation workflows for subscription management.

**Data Sources:** CSV files in `flexiai/toolsmith/data/csv/`

**Use Cases:**
- Customer identification and validation
- Billing inquiry handling
- Service activation/deactivation
- Subscription workflow automation

---

## Security Analysis Tools

### Security Audit

**Tool:** `security_audit`

**Purpose:** Structured security analysis and system inspection through controlled workflows.

> ⚠️ **SECURITY WARNING:** Some operations in this tool can modify system state, require elevated privileges, or trigger security alerts. See [SECURITY.md](../SECURITY.md) for safe usage practices and opt-in requirements.

**Safe Operations (Read-Only):**
- `reconnaissance` – Lists network connections and ARP neighbors
- `detect_processes` – Lists running processes

**Potentially Dangerous Operations:**
- `port_scan` / `network_scan` – May trigger IDS/IPS alerts
- `defense_actions` – **Can modify firewall rules, kill processes, block ports** (requires root/admin)
- `update_system` – **Can trigger system updates** (requires root/admin)

**Configuration:**
- ⚠️ **Note:** Currently, there is no automatic gating for dangerous operations. They will execute if called by an assistant.
- **Recommended:** Implement `ENABLE_DANGEROUS_TOOLS` environment variable check (default: `false`) before production use.
- All `defense_actions` are logged with operator identity and timestamp to `logs/security_audit.log`
- Use only in controlled environments with appropriate permissions

**Operations:**

#### 1. Reconnaissance
- **Operation:** `reconnaissance`
- **Args:** None
- **Result:**
  ```json
  {
    "connections": [
      {"proto": "tcp", "local": "...", "remote": "...", "state": "..."}
    ],
    "neighbors": [
      {"ip": "...", "mac": "...", "state": "REACHABLE"}
    ]
  }
  ```
- **Description:** Lists active network connections and ARP neighbors

#### 2. Process Detection
- **Operation:** `detect_processes`
- **Args:** None
- **Result:**
  ```json
  {
    "processes": [
      {"pid": 1234, "user": "user", "name": "process_name"}
    ]
  }
  ```
- **Description:** Lists running processes

#### 3. Port Scan
- **Operation:** `port_scan`
- **Args:**
  - `target` (str) - Hostname or IP to scan
  - `start_port` (int, optional) - Default: 1
  - `end_port` (int, optional) - Default: 1024
- **Result:**
  ```json
  {
    "target": "192.168.1.1",
    "range": [1, 1024],
    "open_ports": [22, 80, 443],
    "total_open": 3
  }
  ```
- **Description:** Scans TCP ports on target host

#### 4. Network Scan
- **Operation:** `network_scan`
- **Args:**
  - `network` (str, required) - Network CIDR (e.g., "192.168.1.0/24")
- **Result:**
  ```json
  {
    "network": "192.168.1.0/24",
    "alive_hosts": ["192.168.1.1", "192.168.1.100"],
    "total_alive": 2
  }
  ```
- **Description:** Ping-sweep to identify active hosts

#### 5. Defense Actions
- **Operation:** `defense_actions`
- **Args:**
  - `bad_ips` (List[str], optional) - IPs to block
  - `bad_pids` (List[int], optional) - Process IDs to kill
  - `bad_ports` (List[int], optional) - Ports to block
- **Result:**
  ```json
  {
    "blocked_ips": ["1.2.3.4"],
    "killed_pids": [1234],
    "blocked_ports": [8080],
    "errors": []
  }
  ```
- **Description:** Block IPs, kill processes, or block ports

#### 6. System Update
- **Operation:** `update_system`
- **Args:** None
- **Result:**
  ```json
  {
    "ran_as": "root" | "non-root" | "windows",
    "skipped": false,
    "commands": ["apt update", "apt upgrade"]
  }
  ```
- **Description:** Triggers operating system updates

**Infrastructure:**
- Implementation: `security_audit.py`
- Dispatcher: `security_audit_dispatcher()`
- Class: `SecurityAudit`

**Example Usage:**

```python
# Safe operation (read-only)
# Called via ToolsManager.security_audit() which dispatches to security_audit_dispatcher()
result = security_audit(operation="reconnaissance")
# Returns: {"status": True, "message": "...", "result": {"connections": [...], "neighbors": [...]}}

# Port scan (may trigger alerts)
result = security_audit(operation="port_scan", target="192.168.1.1", start_port=1, end_port=1024)
# Returns: {"status": True, "message": "...", "result": {"target": "...", "open_ports": [22, 80, 443], ...}}

# Defense action (requires root/admin, no gating currently)
result = security_audit(operation="defense_actions", bad_ips=["1.2.3.4"], bad_pids=[1234])
# Returns: {"status": True, "message": "Defense complete", "result": {"blocked_ips": [...], "killed_pids": [...], ...}}
# ⚠️ WARNING: This will execute immediately if called. Implement opt-in flag before production.
```

**Note:** Tools are called via the tool registry, which routes to `ToolsManager.security_audit()` method. The method signature is `security_audit(operation: str, **kwargs: Any) -> Dict[str, Any]`.

**Rate Limits & Timeouts:**
- Port scans: Default timeout 1 second per port
- Network scans: Default timeout 1 second per host
- Defense actions: No timeout (executes immediately)
- All operations: Logged to `logs/app.log`

**Security Note:** 
- Defense actions and system updates require appropriate permissions and should be used with caution
- See [SECURITY.md](../SECURITY.md) for complete security guidelines
- ⚠️ **Current Status:** No automatic gating exists. Consider implementing `ENABLE_DANGEROUS_TOOLS` opt-in flag before production use.

---

## Experimental Tools

### Dynamic Web Forms

**Status:** Experimental

**Purpose:** Generate interactive forms inside the web chat UI; submissions are persisted as structured data.

**Features:**
- Dynamic form generation from assistant instructions
- Form submission handling
- Data persistence to CSV
- Web UI integration

**Location:** Handled in `app.py` via `/submit_user_info` endpoint

### OCR Utilities

**Status:** Experimental - not yet integrated

**Purpose:** Optical Character Recognition helpers for image processing.

**Infrastructure:**
- Module: `_recycle/ocr_utils.py`
- Dependencies: `pytesseract`, `Pillow`
- Requirements: Tesseract OCR binary installed

**Note:** This functionality is experimental and not currently integrated into the main tool registry.

---

## Tool Registration

### How Tools Are Registered

1. **ToolsRegistry** (`tools_registry.py`)
   - Maps tool names to callable functions
   - Initialized with `ToolsManager` instance
   - Provides `get_tool(name)` method

2. **ToolsManager** (`tools_manager.py`)
   - Implements core tool functions
   - Dispatches to infrastructure modules
   - Manages tool state and resources

3. **Infrastructure Modules**
   - Specialized implementations (CSV, spreadsheets, security)
   - Entry points route operations to managers
   - Managers perform actual operations

### Adding Custom Tools

To add a custom tool:

1. Implement tool function in `ToolsManager` or create infrastructure module
2. Register in `ToolsRegistry.map_core_tools()` or `map_custom_tools()`
3. Tool becomes available to assistants via tool calls

### Tool Output Format

All tools return structured dictionaries:

```python
{
    "status": bool,      # Success/failure
    "message": str,       # Human-readable summary
    "result": dict | None # Structured data (operation-specific)
}
```

Tool outputs are automatically truncated if they exceed token limits via `context_utils.return_context()`.

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) – System architecture including tool infrastructure
- [WORKFLOW.md](WORKFLOW.md) – Tool execution workflows
- [FILE_MAPPING.md](FILE_MAPPING.md) – Internal file reference
