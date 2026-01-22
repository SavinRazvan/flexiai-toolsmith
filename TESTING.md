# Testing Guide

This document describes how to run tests, write tests, and mock dependencies for FlexiAI Toolsmith.

---

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage
pytest --cov=flexiai --cov-report=html

# Run specific test file
pytest tests/test_tool_executor.py -v
```

---

## Test Structure

> **Note:** A `tests/` directory structure is recommended but not yet fully established. The following structure is suggested:

```
tests/
├── conftest.py              # Shared fixtures
├── test_tool_executor.py    # Tool execution tests
├── test_run_thread_manager.py
├── test_event_handler.py
└── flexiai/
    └── toolsmith/
        └── test_tools_manager.py
```

**Current Status:** Some test files exist in `flexiai/toolsmith/_recycle/` but a comprehensive test suite is not yet established.

---

## Mocking OpenAI API

### Mock AsyncOpenAI Client

```python
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = AsyncMock()
    
    # Mock thread creation
    client.beta.threads.create = AsyncMock(return_value=MagicMock(id="thread_123"))
    
    # Mock run creation
    client.beta.threads.runs.create = AsyncMock(return_value=MagicMock(id="run_456"))
    
    # Mock streaming
    async def mock_stream():
        yield MagicMock(event="thread.message.delta", data=MagicMock(delta=MagicMock(content="Hello")))
        yield MagicMock(event="thread.message.delta", data=MagicMock(delta=MagicMock(content=" World")))
    
    client.beta.threads.runs.stream = AsyncMock(return_value=mock_stream())
    
    return client
```

### Using Mock Client in Tests

```python
@pytest.mark.asyncio
async def test_run_thread_manager(mock_openai_client):
    """Test RunThreadManager with mocked OpenAI client."""
    from flexiai.core.handlers.run_thread_manager import RunThreadManager
    
    manager = RunThreadManager(mock_openai_client)
    thread_id = await manager.get_or_create_thread("user_123")
    
    assert thread_id == "thread_123"
    mock_openai_client.beta.threads.create.assert_called_once()
```

---

## Mocking Tool Execution

### Mock Tools Registry

```python
from unittest.mock import MagicMock
from flexiai.toolsmith.tools_registry import ToolsRegistry

@pytest.fixture
def mock_tools_registry():
    """Create a mock tools registry."""
    registry = MagicMock(spec=ToolsRegistry)
    
    # Mock tool function
    def mock_security_audit(operation, **kwargs):
        return {
            "status": True,
            "message": "Success",
            "result": {"test": "data"}
        }
    
    registry.get_tool.return_value = mock_security_audit
    return registry
```

### Testing Tool Executor

```python
@pytest.mark.asyncio
async def test_tool_executor_executes_tool(mock_tools_registry):
    """Test ToolExecutor with mocked registry."""
    from flexiai.core.handlers.tool_call_executor import ToolCallExecutor
    
    executor = ToolCallExecutor(mock_tools_registry)
    
    tool_call = {
        "id": "call_123",
        "type": "function",
        "function": {
            "name": "security_audit",
            "arguments": '{"operation": "reconnaissance"}'
        }
    }
    
    result = await executor.execute(tool_call)
    
    assert result["status"] is True
    mock_tools_registry.get_tool.assert_called_with("security_audit")
```

---

## Testing Event Handling

### Mock Event Stream

```python
from flexiai.core.events.event_models import MessageDeltaEvent

@pytest.fixture
def mock_event_stream():
    """Create a mock event stream."""
    return [
        MessageDeltaEvent(content="Hello", delta="Hello"),
        MessageDeltaEvent(content=" World", delta=" World"),
        MessageDeltaEvent(content="!", delta="!")
    ]
```

### Testing Event Handler

```python
@pytest.mark.asyncio
async def test_event_handler_processes_stream(mock_event_stream, mock_openai_client):
    """Test EventHandler processes event stream."""
    from flexiai.core.handlers.event_handler import EventHandler
    from flexiai.core.handlers.run_thread_manager import RunThreadManager
    
    run_thread_manager = RunThreadManager(mock_openai_client)
    event_handler = EventHandler(run_thread_manager, ...)
    
    # Process events
    for event in mock_event_stream:
        await event_handler._handle_message_delta(event)
    
    # Verify events were published
    assert event_handler.published_events == len(mock_event_stream)
```

---

## Testing Controllers

### Mock Controller Dependencies

```python
@pytest.fixture
def mock_controller_dependencies():
    """Create all dependencies for controller testing."""
    return {
        "client": mock_openai_client(),
        "run_thread_manager": MagicMock(),
        "event_handler": MagicMock(),
        "tools_manager": MagicMock()
    }
```

### Testing CLI Controller

```python
@pytest.mark.asyncio
async def test_cli_controller_processes_message(mock_controller_dependencies):
    """Test CLIChatController processes user messages."""
    from flexiai.controllers.cli_chat_controller import CLIChatController
    
    controller = CLIChatController(
        assistant_id="test_assistant",
        user_id="test_user",
        **mock_controller_dependencies
    )
    
    await controller.process_user_message("Hello")
    
    # Verify message was added to thread
    mock_controller_dependencies["run_thread_manager"].add_message_to_thread.assert_called_once()
```

---

## Integration Tests

### Testing Full Workflow

```python
@pytest.mark.asyncio
async def test_full_cli_workflow(mock_openai_client):
    """Test complete CLI workflow from message to response."""
    # Setup
    from flexiai.controllers.cli_chat_controller import CLIChatController
    
    controller = await CLIChatController.create_async(
        assistant_id="test",
        user_id="test_user",
        client=mock_openai_client
    )
    
    # Execute
    await controller.process_user_message("Hello")
    
    # Verify
    # Check that thread was created
    # Check that run was started
    # Check that events were published
    # Check that response was received
```

---

## Testing Tools

### Testing CSV Operations

```python
import tempfile
import os
import pytest

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    fd, path = tempfile.mkstemp(suffix='.csv')
    yield path
    os.close(fd)
    os.unlink(path)

def test_csv_operations_create(temp_csv_file):
    """Test CSV create operation."""
    from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.csv_entrypoint import csv_entrypoint
    
    result = csv_entrypoint(
        operation="create",
        path=os.path.dirname(temp_csv_file),
        file_name=os.path.basename(temp_csv_file),
        rows=[{"name": "Alice", "email": "alice@example.com"}]
    )
    
    assert result["status"] is True
    assert os.path.exists(temp_csv_file)
```

### Testing Security Audit

```python
from unittest.mock import patch, MagicMock

@patch('flexiai.toolsmith.tools_infrastructure.security_audit.subprocess')
def test_security_audit_reconnaissance(mock_subprocess):
    """Test security audit reconnaissance operation."""
    from flexiai.toolsmith.tools_infrastructure.security_audit import security_audit_dispatcher
    
    # Mock subprocess output
    mock_subprocess.run.return_value = MagicMock(
        stdout="tcp  0  0 127.0.0.1:8000  0.0.0.0:*  LISTEN"
    )
    
    result = security_audit_dispatcher("reconnaissance")
    
    assert result["status"] is True
    assert "connections" in result["result"]
```

---

## Coverage Goals

- **Overall:** 80%+ coverage
- **Core Handlers:** 90%+ coverage
- **Tool Infrastructure:** 80%+ coverage
- **Controllers:** 75%+ coverage

**View Coverage Report:**
```bash
pytest --cov=flexiai --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled runs (nightly)

**CI Checks:**
- Unit tests
- Integration tests
- Linting (flake8)
- Type checking (mypy, if enabled)

---

## Debugging Tests

### Verbose Output

```bash
pytest -v -s  # Verbose + print statements
pytest --pdb  # Drop into debugger on failure
```

### Test Filtering

```bash
# Run tests matching pattern
pytest -k "tool_executor"

# Run only tests in specific file
pytest tests/test_tool_executor.py

# Run last failed tests
pytest --lf
```

---

## Best Practices

1. **Isolate Tests** – Each test should be independent
2. **Use Fixtures** – Share setup code via pytest fixtures
3. **Mock External Dependencies** – Don't call real APIs in tests
4. **Test Edge Cases** – Empty inputs, None values, exceptions
5. **Keep Tests Fast** – Use mocks, avoid file I/O when possible
6. **Descriptive Names** – Test names should describe what they test

---

## Related Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) – Development guidelines
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) – System architecture
- [docs/WORKFLOW.md](docs/WORKFLOW.md) – Execution workflows
