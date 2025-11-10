# Auto Dashboards Testing Documentation

## Overview

This document describes the comprehensive test suite created for the auto_dashboards JupyterLab extension. The test suite provides thorough coverage of all Python modules in the project.

## Test Files Created

### 1. `tests/test_prompts.py` (67 lines)
Tests the prompt generation functions for converting notebooks to different dashboard types.

**Test Classes:**
- `TestStreamlitPrompt` - Tests Streamlit prompt generation
  - Basic code handling
  - Empty code handling
  - Multiline code preservation
  
- `TestSolaraPrompt` - Tests Solara prompt generation
  - Basic code handling
  - Example code inclusion
  - Component decorator patterns
  
- `TestDashPrompt` - Tests Dash prompt generation
  - Basic code handling
  - Example code with callbacks
  - Command-line argument instructions
  
- `TestPromptComparison` - Cross-framework tests
  - Consistent code handling across all frameworks
  - Framework-specific content verification

**Key Features Tested:**
- Code block formatting
- Framework-specific instructions
- Code preservation and escaping
- Example code inclusion

### 2. `tests/test_process_manager.py` (160 lines)
Tests the dashboard process management system including lifecycle management and URL parsing.

**Test Classes:**
- `TestExtractUrl` - Tests URL extraction from process output
  - HTTP/HTTPS URLs
  - URLs with ports and paths
  - Missing URLs
  - Multiple URLs (first match)
  
- `TestGetOpenPort` - Tests port allocation
  - Returns string type
  - Valid port range (1024-65535)
  - Multiple port allocation
  
- `TestDashboardManager` - Tests singleton manager
  - Singleton pattern enforcement
  - Dashboard lifecycle (start/stop/restart)
  - Support for all dashboard types
  - Existing instance reuse
  - Invalid type handling
  
- `TestStreamlitApplication` - Tests Streamlit integration
  - Initialization and configuration
  - Command generation
  - Process lifecycle
  
- `TestSolaraApplication` - Tests Solara integration
  - Initialization and configuration
  - Command generation with production mode
  
- `TestDashApplication` - Tests Dash integration
  - Initialization and configuration
  - Command generation with proxy path

**Key Features Tested:**
- Process lifecycle management
- Port allocation and management
- URL parsing from different dashboard outputs
- Singleton pattern correctness
- Multi-dashboard support

### 3. `tests/test_handlers.py` (160 lines)
Tests the HTTP API handlers that interface with the JupyterLab frontend.

**Test Classes:**
- `TestRouteHandler` - Tests main routing endpoints
  - GET: List running dashboards
  - POST: Start new dashboard
  - DELETE: Stop dashboard
  - All dashboard types (Streamlit, Solara, Dash)
  
- `TestModelInfoHandler` - Tests model configuration endpoint
  - Default OpenAI model
  - Custom OpenAI models
  - Ollama detection (by URL and name)
  - Local model detection
  - Various Ollama model names
  - Error handling
  
- `TestTranslateHandler` - Tests notebook translation endpoint
  - Missing/invalid JSON payload
  - Invalid notebook paths
  - Successful translations (all types)
  - Missing API credentials
  - Code extraction from code cells
  - Code extraction from markdown cells
  - Markdown code block removal
  - File write errors
  
- `TestSetupHandlers` - Tests handler registration
  - Route registration
  - Custom base URL support

**Key Features Tested:**
- Request/response handling
- Dashboard startup via API
- Notebook parsing and translation
- LLM integration (mocked)
- Model provider detection logic
- Error handling and status codes
- File I/O operations

### 4. Configuration Files

**`pytest.ini`**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
```

**`tests/conftest.py`**
- Sets up Python path for imports
- Can be extended with fixtures and hooks

**`tests/__init__.py`**
- Marks directory as Python package

## Test Coverage Summary

| Module | Lines | Test Lines | Key Areas Covered |
|--------|-------|------------|-------------------|
| `prompts.py` | 67 | 67 | All 3 prompt functions, code handling, examples |
| `process_manager.py` | 298 | 160 | All 4 classes, lifecycle, URL parsing, ports |
| `handlers.py` | 255 | 160 | All 3 handlers, API endpoints, translations |
| **Total** | **620** | **387** | **~62% test-to-code ratio** |

## Running the Tests

### Prerequisites
```bash
# Install test dependencies
pip install -e ".[test]"
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=auto_dashboards --cov-report=term-missing --cov-report=html
```

### Run Specific Test Categories
```bash
# Run only prompt tests
pytest tests/test_prompts.py -v

# Run only process manager tests
pytest tests/test_process_manager.py -v

# Run only handler tests
pytest tests/test_handlers.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_prompts.py::TestStreamlitPrompt -v
```

### Run Specific Test Method
```bash
pytest tests/test_prompts.py::TestStreamlitPrompt::test_streamlit_prompt_basic_code -v
```

## Test Patterns and Best Practices

### 1. Mocking External Dependencies
All tests use `unittest.mock` to mock external dependencies:
- `Popen` for process management
- `OpenAI` client for LLM calls
- File I/O operations
- Environment variables

### 2. Test Organization
- One test class per component/feature
- Clear, descriptive test names
- Setup/teardown methods where needed
- Tests grouped by functionality

### 3. Coverage Goals
- Happy paths (normal operation)
- Edge cases (empty inputs, special characters)
- Error conditions (missing files, invalid data)
- Different configurations (models, frameworks)

### 4. Assertions
- Specific assertions for expected behavior
- Error message validation
- Return type checking
- State verification

## Integration with CI/CD

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[test]"
    pytest --cov=auto_dashboards --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Future Test Enhancements

Potential areas for additional testing:
1. **TypeScript Tests** - Add Jest/Mocha tests for frontend code
2. **Integration Tests** - End-to-end tests with real JupyterLab
3. **Performance Tests** - Load testing for multiple dashboards
4. **Async Tests** - Test concurrent dashboard operations
5. **Security Tests** - Input validation and sanitization

## Maintenance

### Adding New Tests
When adding new features, follow this pattern:

```python
class TestNewFeature:
    def setup_method(self):
        # Setup test fixtures
        pass
    
    def test_feature_happy_path(self):
        # Test normal operation
        pass
    
    def test_feature_edge_case(self):
        # Test edge cases
        pass
    
    def test_feature_error_handling(self):
        # Test error conditions
        pass
```

### Updating Existing Tests
- Keep tests focused and independent
- Update mocks when external APIs change
- Maintain test documentation
- Run full suite before committing

## Contact and Support

For questions or issues with the test suite:
- Review test documentation in `tests/README.md`
- Check test output for detailed error messages
- Refer to pytest documentation for advanced usage