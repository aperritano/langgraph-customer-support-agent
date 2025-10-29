# Quick Start Guide

Get the customer support bot running in 5 minutes!

## Step 1: Install Ollama

### macOS
```bash
brew install ollama
ollama serve
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### Windows
Download from https://ollama.ai/download/windows

## Step 2: Pull Model

```bash
ollama pull llama3.2:3b
```

## Step 3: Setup Project

```bash
cd customer-support-bot

# Create virtual environment
python -m venv venv

# Activate (choose your OS)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install langgraph-cli
```

## Step 4: Run the Bot

### Option A: LangGraph Studio (Visual Interface)

```bash
langgraph dev
```

Then open: http://127.0.0.1:8123

### Option B: CLI (Command Line)

```bash
python scripts/cli.py
```

### Option C: Test Suite

```bash
python scripts/test_bot.py
```

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
**Fix**: Make sure you're in the project root directory

**Issue**: Ollama connection error
**Fix**: 
```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve
```

**Issue**: Model not found
**Fix**: 
```bash
ollama pull llama3.2:3b
```

**Issue**: Port 8123 already in use
**Fix**: 
```bash
langgraph dev --port 8124
```

## Next Steps

1. Try different test conversations
2. Modify the system prompt in `src/support_agent/prompts.py`
3. Add new tools in `src/support_agent/tools.py`
4. Customize the knowledge base data
5. Build a web UI on top of the API

## Example Queries to Try

- "What's your return policy?"
- "Can you check order #123456?"
- "I want to return my order because it's defective"
- "Do you have laptops in stock?"
- "This is terrible service! I want to speak to a manager!"

## API Usage

```python
import requests

# Create conversation
response = requests.post("http://localhost:8123/threads")
thread_id = response.json()["thread_id"]

# Send message
response = requests.post(
    f"http://localhost:8123/threads/{thread_id}/runs",
    json={
        "input": {
            "messages": [{"role": "user", "content": "What's your return policy?"}]
        }
    }
)

print(response.json())
```

Happy coding! 🚀
