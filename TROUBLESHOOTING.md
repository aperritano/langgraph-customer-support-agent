# Troubleshooting Guide

Common issues and solutions for the Customer Support Bot.

## Installation Issues

### Python Version Error

**Error**: `requires-python = ">=3.11"`

**Solution**:
```bash
# Check your Python version
python --version

# If < 3.11, install newer Python
# macOS:
brew install python@3.11

# Linux:
sudo apt install python3.11

# Windows: Download from python.org
```

### ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'langgraph'`

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Import Error from 'src'

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Make sure you're in the project root
pwd  # Should show: .../customer-support-bot

# Install package in editable mode
pip install -e .

# Or run scripts with full path
python -m scripts.cli
```

## Ollama Issues

### Ollama Not Running

**Error**: `Connection refused` or `Failed to connect to Ollama`

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# On macOS, you can also:
brew services start ollama
```

### Model Not Found

**Error**: `Model 'llama3.2:3b' not found`

**Solution**:
```bash
# Pull the model
ollama pull llama3.2:3b

# Verify it's installed
ollama list

# If you want a different model
ollama pull mistral:7b
# Then update src/support_agent/agent.py
```

### Ollama Running but Not Responding

**Solution**:
```bash
# Check Ollama logs
tail -f ~/.ollama/logs/server.log

# Restart Ollama
pkill ollama
ollama serve

# Test Ollama directly
curl http://localhost:11434/api/tags
```

## LangGraph Dev Issues

### Port Already in Use

**Error**: `Address already in use: 8123`

**Solution**:
```bash
# Option 1: Use different port
langgraph dev --port 8124

# Option 2: Find and kill process using port 8123
# macOS/Linux:
lsof -ti:8123 | xargs kill -9

# Windows:
netstat -ano | findstr :8123
taskkill /PID <PID> /F
```

### Graph Not Found

**Error**: `Graph 'support_agent' not found`

**Solution**:
```bash
# Verify langgraph.json is correct
cat langgraph.json

# Make sure file paths are correct
# Should be: "./src/support_agent/agent.py:graph"

# Try absolute import
python -c "from src.support_agent.agent import graph; print(graph)"
```

### Changes Not Reflecting

**Issue**: Code changes not appearing in LangGraph Studio

**Solution**:
```bash
# LangGraph Dev auto-reloads, but if stuck:
# 1. Stop server (Ctrl+C)
# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
# 3. Restart
langgraph dev
```

## Runtime Issues

### Agent Not Using Tools

**Issue**: Bot responds without calling tools

**Possible Causes**:
1. **Ollama model doesn't support tool calling well**
   - Solution: Use llama3.2:3b, mistral:7b, or qwen2.5:7b
   - These models have better tool calling support

2. **System prompt unclear**
   - Solution: Make tool usage more explicit in prompts.py

3. **Tools not properly bound**
   - Check: `llm.bind_tools(tools)` in agent.py

**Debug**:
```python
# Test tool calling directly
from src.support_agent.agent import llm
result = llm.invoke("Use get_order_status for order #123456")
print(result.tool_calls)  # Should not be empty
```

### Slow Responses

**Issue**: Bot takes too long to respond

**Solutions**:
```bash
# 1. Use faster model
# Edit src/support_agent/agent.py
llm = ChatOllama(model="llama3.2:3b")  # Fastest

# 2. Check Ollama performance
ollama run llama3.2:3b "Hello"  # Should be fast

# 3. Reduce context
# Limit conversation history if too long

# 4. Check system resources
htop  # macOS/Linux
# Task Manager (Windows)
# Ollama needs RAM for models
```

### Memory/State Issues

**Issue**: Bot doesn't remember previous messages

**Solution**:
```python
# Check if checkpointer is configured
# In agent.py, verify:
memory = SqliteSaver.from_conn_string("...")
graph = workflow.compile(checkpointer=memory)

# Check if thread_id is consistent
# In CLI/API, make sure thread_id stays the same

# Verify checkpoint file
ls -lh storage/checkpoints.db
```

### Tool Execution Errors

**Issue**: Tools failing silently

**Debug**:
```bash
# Run with more logging
export LANGCHAIN_VERBOSE=true
python scripts/cli.py

# Or add print statements in tools.py
@tool
def my_tool(param: str) -> str:
    print(f"DEBUG: Tool called with {param}")
    # ... rest of tool
```

## API Issues

### API Returns 404

**Error**: `404 Not Found`

**Solution**:
```bash
# Check base URL
curl http://localhost:8123/health

# Verify thread exists before sending message
# Create thread first:
curl -X POST http://localhost:8123/threads

# Check LangGraph Dev is running
ps aux | grep langgraph
```

### API Returns 500

**Error**: `500 Internal Server Error`

**Solution**:
```bash
# Check LangGraph Dev logs
# They print to terminal where you ran 'langgraph dev'

# Common causes:
# 1. Ollama not running
# 2. Model not loaded
# 3. Tool error

# Test with curl
curl -X POST http://localhost:8123/threads/test/runs \
  -H "Content-Type: application/json" \
  -d '{"input": {"messages": [{"role": "user", "content": "test"}]}}'
```

### Streaming Not Working

**Issue**: Can't stream responses

**Solution**:
```python
# Make sure to set stream_mode
payload = {
    "input": {"messages": [...]},
    "stream_mode": "values"  # or "updates"
}

# Use requests with stream=True
response = requests.post(url, json=payload, stream=True)
for line in response.iter_lines():
    # Process line
```

## Docker Issues

### Container Won't Start

**Error**: `Container exits immediately`

**Solution**:
```bash
# Check logs
docker logs support-bot

# Common issues:
# 1. Ollama not accessible
docker-compose logs ollama

# 2. Port conflict
docker-compose down
docker-compose up  # Check for port errors

# 3. Permission issues
chmod -R 755 storage/
```

### Can't Connect to Ollama in Docker

**Solution**:
```bash
# Verify network
docker network ls
docker network inspect customer-support-bot_support-network

# Check if services can communicate
docker-compose exec support-bot ping ollama

# Verify OLLAMA_BASE_URL
docker-compose exec support-bot env | grep OLLAMA
```

## Performance Optimization

### Reduce Memory Usage

```python
# Use smaller model
llm = ChatOllama(model="llama3.2:1b")

# Limit conversation history
def agent_node(state: SupportState) -> dict:
    # Keep only last 10 messages
    messages = state["messages"][-10:]
    # ... rest of function
```

### Speed Up Tool Execution

```python
# Use async tools
@tool
async def fast_tool(param: str) -> str:
    """Async tool."""
    result = await async_operation(param)
    return result

# Cache results
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_lookup(key: str) -> str:
    # Expensive operation
    return result
```

## Getting More Help

Still stuck? Try these resources:

1. **Check Documentation**
   - [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
   - [Ollama Docs](https://ollama.ai/docs)

2. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Run with Verbose Mode**
   ```bash
   export LANGCHAIN_VERBOSE=true
   export LANGCHAIN_TRACING_V2=true
   ```

4. **Check GitHub Issues**
   - LangGraph issues
   - Ollama issues

5. **Community Support**
   - LangChain Discord
   - Stack Overflow

## Reporting Bugs

When reporting issues, include:

1. **Environment**
   ```bash
   python --version
   ollama --version
   pip list | grep lang
   ```

2. **Error Message**
   - Full stack trace
   - LangGraph Dev logs

3. **Steps to Reproduce**
   - Exact commands run
   - Input that caused error

4. **Expected vs Actual**
   - What should happen
   - What actually happened

Good luck! 🚀
