# Auto Dashboards Test Suite

This directory contains comprehensive unit tests for the auto_dashboards JupyterLab extension.

## Test Structure

- `test_prompts.py` - Tests for prompt generation functions (streamlit, solara, dash)
- `test_process_manager.py` - Tests for dashboard process management and lifecycle
- `test_handlers.py` - Tests for HTTP API handlers and request processing
- `conftest.py` - Pytest configuration and fixtures
- `../pytest.ini` - Pytest settings and markers

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_prompts.py
pytest tests/test_process_manager.py
pytest tests/test_handlers.py
```

### Run with coverage:
```bash
pytest --cov=auto_dashboards --cov-report=html
```

### Run specific test class:
```bash
pytest tests/test_prompts.py::TestStreamlitPrompt
```

### Run specific test:
```bash
pytest tests/test_prompts.py::TestStreamlitPrompt::test_streamlit_prompt_basic_code
```

## Test Coverage

The test suite covers:
- ✅ Prompt generation for all dashboard types (Streamlit, Solara, Dash)
- ✅ Dashboard process lifecycle (start, stop, restart)
- ✅ Port management and URL extraction
- ✅ HTTP API handlers (GET, POST, DELETE)
- ✅ Model provider detection (OpenAI, Ollama, local)
- ✅ Notebook translation and code extraction
- ✅ Error handling and edge cases
- ✅ Singleton pattern for DashboardManager
- ✅ Multi-dashboard support

## Requirements

Test dependencies are specified in `pyproject.toml` under `[project.optional-dependencies]`:
```toml
test = [
    "coverage",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-jupyter[server]>=0.6.0"
]
```

Install test dependencies:
```bash
pip install -e ".[test]"
```