# Support Agent Tests

This directory contains TDD (Test-Driven Development) tests for the customer support agent implementation.

## Test Structure

```
tests/
├── __init__.py           # Package initialization
├── conftest.py           # Pytest configuration and fixtures
├── test_agent.py         # Tests for agent graph logic
├── test_tools.py         # Tests for support tools
├── test_state.py         # Tests for state management
└── README.md            # This file
```

## Test Categories

### Unit Tests (Fast)
- **test_state.py**: State management and message handling
- **test_tools.py**: Individual tool functionality
- **test_agent.py**: Agent decision logic (should_continue)

### Integration Tests (Slower, require LLM)
- **test_agent.py** (marked with `@pytest.mark.integration`): Full graph execution tests

## Setup

### Prerequisites

Before running tests, ensure you have the dependencies installed:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -e ".[dev]"
# OR install just pytest
pip install pytest pytest-cov
```

## Running Tests

**Important**: Always activate the virtual environment first!

```bash
source .venv/bin/activate
```

### Run all tests
```bash
pytest src/support_agent/tests/
```

### Run only unit tests (fast)
```bash
pytest src/support_agent/tests/ -m "not integration"
```

### Run only integration tests
```bash
pytest src/support_agent/tests/ -m integration
```

### Run specific test file
```bash
pytest src/support_agent/tests/test_tools.py
```

### Run specific test class
```bash
pytest src/support_agent/tests/test_tools.py::TestGetOrderStatus
```

### Run specific test
```bash
pytest src/support_agent/tests/test_tools.py::TestGetOrderStatus::test_get_order_status_in_transit
```

### Run with verbose output
```bash
pytest src/support_agent/tests/ -v
```

### Run with coverage report
```bash
pytest src/support_agent/tests/ --cov=src.support_agent --cov-report=html
```

## Test Coverage

The tests cover the following key aspects:

### Agent Graph Logic (`test_agent.py`)
- ✅ Conditional routing (should_continue)
- ✅ Agent node message handling
- ✅ Graph structure and compilation
- ✅ End-to-end conversation flows (integration)

### Support Tools (`test_tools.py`)
- ✅ Order status lookup (in-transit, delivered, processing)
- ✅ Return initiation (defective vs regular returns)
- ✅ Product availability checking (in-stock, low-stock, out-of-stock)
- ✅ Human escalation (different scenarios)
- ✅ Mock data integrity

### State Management (`test_state.py`)
- ✅ State schema validation
- ✅ Message accumulation (add_messages)
- ✅ Multiple message type handling
- ✅ Message attribute preservation
- ✅ Conversation flow through states

## Writing New Tests

When adding new functionality, follow TDD principles:

1. **Write the test first** - Define expected behavior
2. **Run the test** - Verify it fails (red)
3. **Implement the feature** - Make it work
4. **Run the test again** - Verify it passes (green)
5. **Refactor** - Clean up while keeping tests green

### Example Test Template

```python
class TestNewFeature:
    """Test description of the feature."""

    def test_basic_functionality(self):
        """Test basic happy path."""
        # Arrange
        input_data = "test input"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected_output

    def test_edge_case(self):
        """Test edge case handling."""
        # Test edge case
        pass

    def test_error_handling(self):
        """Test error handling."""
        # Test error scenarios
        pass
```

## Integration Test Notes

Integration tests marked with `@pytest.mark.integration` require:
- Running Ollama with llama3.1:latest model
- Network connectivity (if using real APIs)
- Longer execution time

Skip integration tests for quick development cycles:
```bash
pytest src/support_agent/tests/ -m "not integration"
```

## Continuous Integration

For CI/CD pipelines, consider:
- Running unit tests on every commit
- Running integration tests on pull requests
- Setting up test coverage thresholds
- Mocking LLM calls for faster CI execution

## Mocking Guidelines

For unit tests, mock external dependencies:
```python
from unittest.mock import Mock, patch

@patch('src.support_agent.agent.llm')
def test_with_mocked_llm(mock_llm):
    mock_llm.invoke.return_value = AIMessage(content="Mocked response")
    # Test logic
```

## Fixtures

Common fixtures are available in `conftest.py`:
- `sample_human_message`: Basic human message
- `sample_ai_message`: Basic AI response
- `sample_ai_message_with_tool_call`: AI message with tool calls
- `sample_tool_message`: Tool execution result
- `basic_conversation_state`: Multi-turn conversation state

Use fixtures to keep tests DRY (Don't Repeat Yourself).
