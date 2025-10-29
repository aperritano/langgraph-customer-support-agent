# Quick Start - Running Tests

## The Issue You Encountered

If you see this error:
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution**: You need to activate the virtual environment first!

## Step-by-Step Instructions

### 1. Activate Virtual Environment

From the project root directory:

```bash
source .venv/bin/activate
```

You should see `(.venv)` appear in your terminal prompt.

### 2. Verify Dependencies

Check that pytest is installed:

```bash
which pytest
# Should show: /Users/.../langgraph-customer-support-agent/.venv/bin/pytest
```

If pytest is not installed:

```bash
pip install pytest pytest-cov
```

### 3. Run the Tests

Now run the tests:

```bash
# Run unit tests only (recommended - fast!)
pytest src/support_agent/tests/ -m "not integration"

# Or run all tests
pytest src/support_agent/tests/
```

### Expected Output

You should see:
```
============================= test session starts ==============================
...
collected 53 items / 3 deselected / 50 selected

src/support_agent/tests/test_agent.py ..........                         [ 20%]
src/support_agent/tests/test_state.py ..............                     [ 48%]
src/support_agent/tests/test_tools.py ..........................         [100%]

================= 50 passed, 3 deselected, 1 warning in 13.70s =================
```

## One-Liner Commands

### Quick test run (from project root):
```bash
source .venv/bin/activate && pytest src/support_agent/tests/ -m "not integration"
```

### With verbose output:
```bash
source .venv/bin/activate && pytest src/support_agent/tests/ -m "not integration" -v
```

### Run specific test file:
```bash
source .venv/bin/activate && pytest src/support_agent/tests/test_tools.py -v
```

### Run specific test:
```bash
source .venv/bin/activate && pytest src/support_agent/tests/test_tools.py::TestGetOrderStatus::test_get_order_status_in_transit -v
```

## Troubleshooting

### Problem: "command not found: pytest"
**Solution**: Virtual environment not activated or pytest not installed
```bash
source .venv/bin/activate
pip install pytest pytest-cov
```

### Problem: "ModuleNotFoundError: No module named 'langgraph'"
**Solution**: Virtual environment not activated
```bash
source .venv/bin/activate
```

### Problem: Tests fail with LLM errors
**Solution**: You're running integration tests that need Ollama. Skip them:
```bash
pytest src/support_agent/tests/ -m "not integration"
```

## Test Organization

- **50 unit tests** - Fast, no external dependencies (LLM not required)
- **3 integration tests** - Slower, require Ollama with llama3.1:latest

Default: Run unit tests only for quick feedback during development.
