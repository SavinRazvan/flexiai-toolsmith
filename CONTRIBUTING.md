# Contributing to FlexiAI Toolsmith

Thank you for your interest in contributing! This document provides guidelines for development, testing, and submission.

---

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Basic understanding of async Python, Quart, and OpenAI Assistant API

### Initial Setup

```bash
# Clone repository
git clone https://github.com/SavinRazvan/flexiai-toolsmith.git
cd flexiai-toolsmith

# Set up environment
./setup_env.sh

# Activate environment
source .venv/bin/activate  # or conda activate .conda_flexiai

# Install development dependencies
pip install -r requirements.txt
```

---

## Code Style

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function signatures
- Maximum line length: **100 characters** (soft limit)
- Use **black**-compatible formatting (4 spaces, no tabs)

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `RunThreadManager`)
- **Functions/Methods:** `snake_case` (e.g., `create_thread`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private methods:** Prefix with `_` (e.g., `_handle_message_delta`)

### Documentation

- Use **docstrings** for all public functions and classes
- Follow **Google-style** docstrings:
  ```python
  def create_thread(user_id: str) -> str:
      """Create a new assistant thread.
      
      Args:
          user_id: Unique identifier for the user.
          
      Returns:
          Thread ID from OpenAI API.
          
      Raises:
          ValueError: If user_id is empty.
      """
  ```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flexiai --cov-report=html

# Run specific test file
pytest tests/test_tool_executor.py

# Run with verbose output
pytest -v
```

### Writing Tests

> **Note:** A `tests/` directory structure is recommended but not yet established. Tests can be placed in:
> - `tests/` directory (to be created)
> - Mirror source structure (e.g., `tests/flexiai/core/handlers/`)
> - Use descriptive test names: `test_tool_executor_handles_exception`
> - Mock external dependencies (OpenAI API, file system)

**Example Test:**
```python
import pytest
from unittest.mock import AsyncMock, patch
from flexiai.core.handlers.tool_call_executor import ToolCallExecutor

@pytest.mark.asyncio
async def test_tool_executor_executes_tool():
    """Test that ToolExecutor correctly executes a tool."""
    registry = MockToolsRegistry()
    executor = ToolCallExecutor(registry)
    
    result = await executor.execute({
        "name": "test_tool",
        "arguments": '{"param": "value"}'
    })
    
    assert result["status"] is True
    assert "result" in result
```

### Test Coverage

- Aim for **80%+ coverage** for new code
- Focus on critical paths (tool execution, event handling)
- Mock external APIs and file operations

---

## Linting

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Linters Used

- **flake8** – Style and error checking
- **mypy** – Type checking (optional, but recommended)
- **black** – Code formatting (check only, no auto-format)

**Run Linters:**
```bash
# Check style
flake8 flexiai/

# Type check (if mypy is installed)
mypy flexiai/

# Format check
black --check flexiai/
```

---

## Branch Naming

Use descriptive branch names:

- `feature/add-csv-validation` – New features
- `fix/tool-executor-timeout` – Bug fixes
- `docs/update-architecture` – Documentation
- `refactor/event-handler` – Code refactoring

---

## Pull Request Process

### Before Submitting

1. **Update Documentation**
   - Update relevant docs in `docs/`
   - Add/update docstrings
   - Update CHANGELOG.md if applicable

2. **Run Tests**
   ```bash
   pytest
   flake8 flexiai/
   ```

3. **Test Your Changes**
   - Test CLI: `python chat.py`
   - Test Web: `hypercorn app:app --bind 127.0.0.1:8000`
   - Verify tool execution works

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No linter errors
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Security considerations addressed (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Related Issues
Closes #123
```

---

## Architecture Guidelines

### Adding New Tools

1. **Implement in `tools_manager.py`** or create infrastructure module
2. **Register in `tools_registry.py`**
3. **Add documentation** in `docs/TOOLING.md`
4. **Add tests** in `tests/flexiai/toolsmith/`
5. **Update security docs** if tool has security implications

### Adding New Channels

1. **Extend `BaseChannel`** in `flexiai/channels/`
2. **Register in `channel_manager.py`**
3. **Add to `ACTIVE_CHANNELS`** configuration
4. **Add tests** for channel publishing

### Modifying Core Handlers

- Maintain interface contracts (see `docs/ARCHITECTURE.md`)
- Update tests for interface changes
- Document breaking changes in CHANGELOG.md

---

## Security Considerations

### For Contributors

- **Never commit** API keys, credentials, or `.env` files
- **Review security implications** of new tools (see `SECURITY.md`)
- **Add security warnings** for dangerous operations
- **Test in isolated environments** before production

### Security Review

PRs that add or modify:
- Security audit tools
- Network operations
- File system operations
- Authentication/authorization

Will require additional security review.

---

## Documentation

### Updating Documentation

- **README.md** – Overview and quick start only
- **docs/ARCHITECTURE.md** – System architecture
- **docs/WORKFLOW.md** – Execution flows
- **docs/TOOLING.md** – Tool capabilities
- **docs/ENV_SETUP.md** – Environment setup
- **SECURITY.md** – Security guidelines

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep examples runnable and up-to-date
- Link between related documents

---

## Getting Help

- **Questions?** Open a discussion or issue
- **Bug Reports?** Use the issue template
- **Feature Requests?** Open an issue with the feature label

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

Thank you for contributing to FlexiAI Toolsmith! 🚀
