# Customer Service Support Bot

A production-ready customer support agent built with LangGraph, featuring intelligent tool calling, conversation memory, and local LLM support via Ollama.

## Features

- 🤖 **Intelligent Agent**: Uses ReAct pattern with tool calling
- 💬 **Multi-turn Conversations**: Built-in memory with SQLite
- 🔧 **5 Support Tools**: Knowledge base, order tracking, returns, inventory, escalation
- 🎨 **LangGraph Studio**: Visual debugging and testing UI
- 🚀 **Local First**: Runs entirely on your machine with Ollama
- 📊 **REST API**: Auto-generated endpoints via LangGraph Dev

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- Node.js/pnpm (optional, for TypeScript projects)

## Quick Start

### 1. Install Ollama and Pull Model

```bash
# Install Ollama from https://ollama.ai

# Pull a model (choose one)
ollama pull llama3.2:3b      # Recommended - fast and efficient
ollama pull mistral:7b       # Alternative
ollama pull qwen2.5:7b       # Alternative
```

### 2. Clone and Setup

```bash
# Navigate to project directory
cd customer-support-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install LangGraph CLI
pip install langgraph-cli
```

### 3. Run the Bot

**Option A: LangGraph Studio (Recommended)**

```bash
# Start the development server
langgraph dev

# Open browser to: http://127.0.0.1:8123
# You'll see a visual interface with chat, graph view, and debugging tools
```

**Option B: Command Line Interface**

```bash
# Interactive CLI chat
python scripts/cli.py
```

**Option C: Test Script**

```bash
# Run automated tests
python scripts/test_bot.py
```

## Project Structure

```
customer-support-bot/
├── src/
│   └── support_agent/
│       ├── __init__.py         # Package init
│       ├── agent.py            # Main graph definition
│       ├── state.py            # State schema
│       ├── tools.py            # Tool implementations
│       └── prompts.py          # System prompts
├── scripts/
│   ├── cli.py                  # Interactive CLI
│   └── test_bot.py             # Test conversations
├── storage/                    # Created on first run
│   └── checkpoints.db          # Conversation memory
├── data/
│   └── knowledge_base.json     # Mock KB data
├── langgraph.json              # LangGraph config
├── pyproject.toml              # Project metadata
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Usage Examples

### Using LangGraph Studio

1. Start server: `langgraph dev`
2. Open http://127.0.0.1:8123
3. Type messages in the chat interface
4. Watch tool calls happen in real-time
5. Inspect state at each step

### Using CLI

```bash
python scripts/cli.py

# Example conversation:
You: Hi, what's your return policy?
🤖 Bot: We accept returns within 30 days of delivery...

You: Can you check order #123456?
🔧 Using tool: get_order_status...
🤖 Bot: Order #123456 is in transit...
```

### Using the API

```python
import requests

# Create thread
response = requests.post("http://localhost:8123/threads")
thread_id = response.json()["thread_id"]

# Send message
requests.post(
    f"http://localhost:8123/threads/{thread_id}/runs",
    json={
        "input": {
            "messages": [{"role": "user", "content": "What's your return policy?"}]
        }
    }
)
```

## Available Tools

The bot has access to these tools:

1. **search_knowledge_base** - Find store policies and FAQ
2. **get_order_status** - Look up order tracking
3. **initiate_return** - Start return process
4. **check_product_availability** - Check stock levels
5. **escalate_to_human** - Transfer to human agent

## Configuration

### Change LLM Model

Edit `src/support_agent/agent.py`:

```python
llm = ChatOllama(
    model="mistral:7b",  # Change this
    temperature=0
)
```

### Customize Knowledge Base

Edit `data/knowledge_base.json` to add your own policies and FAQ.

### Add New Tools

1. Add tool to `src/support_agent/tools.py`:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description."""
    return "result"
```

2. Add to tools list:
```python
tools = [
    search_knowledge_base,
    get_order_status,
    # ... existing tools
    my_new_tool  # Add here
]
```

3. Restart server - that's it!

## Troubleshooting

**Ollama not running:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve
```

**Model not found:**
```bash
# Pull the model
ollama pull llama3.2:3b
```

**Port already in use:**
```bash
# Use different port
langgraph dev --port 8124
```

**Dependencies issues:**
```bash
# Reinstall clean
pip install --upgrade --force-reinstall -r requirements.txt
```

## Development

### Running Tests

```bash
# Run test conversations
python scripts/test_bot.py

# Add your own tests in scripts/test_bot.py
```

### Hot Reload

LangGraph Dev automatically reloads when you change code. Just save your files and test immediately.

### Debugging

Use LangGraph Studio to:
- Set breakpoints on nodes
- Step through execution
- Inspect state at any point
- Time-travel debug (rewind and replay)

## Deployment

### Local Production

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.support_agent.agent:app
```

### Docker

```bash
# Build image
docker build -t support-bot .

# Run container
docker run -p 8123:8123 support-bot
```

### LangGraph Cloud

```bash
# Deploy to LangGraph Cloud
langgraph deploy
```

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions:
- Check the [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- Open an issue on GitHub
- Review example conversations in `scripts/test_bot.py`

## Next Steps

- [ ] Add RAG with vector database (ChromaDB)
- [ ] Integrate with real order management system
- [ ] Add sentiment analysis for escalation
- [ ] Create web UI with React
- [ ] Add authentication and user management
