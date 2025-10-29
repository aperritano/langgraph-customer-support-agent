# Customer Support Bot

A production-ready customer support agent built with LangGraph, featuring intelligent tool calling, conversation memory, and local LLM support via Ollama.

## 🎉 What You Have

A complete, production-ready customer support agent built with:
- ✅ LangGraph for orchestration
- ✅ Local LLM via Ollama (privacy-first)
- ✅ 5 pre-built tools (order tracking, returns, KB search, etc.)
- ✅ Visual debugging with LangGraph Studio
- ✅ REST API ready to use
- ✅ Full documentation and examples
- ✅ Vector store implementation for semantic search

## Features

- 🤖 **Intelligent Agent**: Uses ReAct pattern with tool calling
- 💬 **Multi-turn Conversations**: Built-in memory with SQLite
- 🔧 **5 Support Tools**: Knowledge base, order tracking, returns, inventory, escalation
- 🎨 **LangGraph Studio**: Visual debugging and testing UI
- 🚀 **Local First**: Runs entirely on your machine with Ollama
- 📊 **REST API**: Auto-generated endpoints via LangGraph Dev
- 🔍 **Semantic Search**: Vector-based knowledge base search

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- Node.js/pnpm (optional, for TypeScript projects)

## 🚀 Get Started in 3 Steps

### Step 1: Install Ollama (2 minutes)

**macOS:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**Windows:**
Download from https://ollama.ai/download/windows

**Pull the model:**
```bash
ollama pull llama3.2:3b
```

### Step 2: Setup Python Environment (1 minute)

```bash
cd customer-support-bot

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install langgraph-cli
```

### Step 3: Run It! (30 seconds)

**Option A: Visual Interface (Recommended)**
```bash
langgraph dev
```
Then open: http://127.0.0.1:8123

**Option B: Command Line**
```bash
python scripts/cli.py
```

**Option C: Run Tests**
```bash
python scripts/test_bot.py
```

## 📁 Project Structure

```
customer-support-bot/
├── 📖 Documentation
│   ├── README.md                  # This file - complete documentation
│   ├── LICENSE                    # MIT License
│   └── .gitignore                # Git ignore patterns
│
├── 🐍 Python Application
│   ├── src/support_agent/         ⚙️ Main application code
│   │   ├── __init__.py           
│   │   ├── agent.py              🎯 CORE: Graph definition
│   │   ├── tools.py              🔧 5 support tools
│   │   ├── state.py              💾 State schema
│   │   ├── prompts.py            💬 System instructions
│   │   └── vector_store.py       🔍 Vector search implementation
│   │
│   └── scripts/                   🎬 Ready-to-run scripts
│       ├── cli.py                 💻 Interactive chat
│       ├── test_bot.py            🧪 Test suite
│       ├── api_client_example.py 📡 API examples
│       └── init_vector_store.py  🔍 Vector store testing
│
├── 📊 Data
│   └── data/
│       └── knowledge_base.json    📚 Mock KB data
│
├── ⚙️ Configuration
│   ├── langgraph.json             🔗 LangGraph config (required!)
│   ├── pyproject.toml             📦 Project metadata
│   ├── requirements.txt            📋 Dependencies
│   └── .env.example               🔐 Environment template
│
├── 🐳 Docker (Optional)
│   ├── Dockerfile                 📦 Container image
│   └── docker-compose.yml         🎼 Multi-container setup
│
└── 📁 Storage (Generated at Runtime)
    └── storage/                   # Created automatically
        └── checkpoints.db         # SQLite database for conversation memory
```

### Key Files

**agent.py** - The heart of the application
- Defines the LangGraph workflow
- Creates agent and tool nodes
- Implements ReAct loop (reasoning + acting)
- Exports `graph` variable for LangGraph Dev

**tools.py** - Business logic
- `search_knowledge_base()` - Find policies and FAQ using vector search
- `get_order_status()` - Look up orders
- `initiate_return()` - Process returns
- `check_product_availability()` - Check inventory
- `escalate_to_human()` - Create support tickets

**state.py** - Data schema
- Defines `SupportState` TypedDict
- Manages conversation history with `add_messages`

**prompts.py** - Agent instructions
- System prompt that guides agent behavior
- Defines when to use tools
- Sets tone and guidelines

**vector_store.py** - Semantic search
- Implements vector-based knowledge base search
- Uses HuggingFace embeddings for semantic understanding
- Provides intelligent document retrieval

## 🎯 Try These First

Once running, try these example queries:

1. "What's your return policy?"
2. "Can you check order #123456?"
3. "I want to return my order because it's defective"
4. "Do you have laptops in stock?"
5. "This is terrible service!" (watch it escalate!)

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

1. **search_knowledge_base** - Find store policies and FAQ using semantic search
2. **get_order_status** - Look up order tracking
3. **initiate_return** - Start return process
4. **check_product_availability** - Check stock levels
5. **escalate_to_human** - Transfer to human agent

## 🔧 Customization

### Adding a New Tool

Tools are how the agent interacts with external systems. Here's how to add one:

#### 1. Define the Tool

Edit `src/support_agent/tools.py`:

```python
@tool
def your_new_tool(param1: str, param2: int = 0) -> str:
    """Short description of what the tool does.
    
    Use this tool when:
    - Situation 1
    - Situation 2
    
    Args:
        param1: Description of parameter
        param2: Optional parameter with default
    
    Returns:
        Description of what the tool returns
    """
    # Your implementation here
    result = do_something(param1, param2)
    return f"Result: {result}"
```

#### 2. Add to Tools List

At the bottom of `tools.py`:

```python
tools = [
    search_knowledge_base,
    get_order_status,
    # ... existing tools
    your_new_tool,  # Add here
]
```

#### 3. Test It

```python
python scripts/test_bot.py
```

That's it! The agent will automatically learn to use your tool.

### Modifying the System Prompt

The system prompt guides the agent's behavior.

Edit `src/support_agent/prompts.py`:

```python
SYSTEM_PROMPT = """You are a helpful customer support agent...

Your job is to:
1. [Add your custom instructions]
2. [More instructions]
...
"""
```

### Changing the LLM Model

Edit `src/support_agent/agent.py`:

```python
llm = ChatOllama(
    model="mistral:7b",  # Change this
    temperature=0.3,      # Adjust creativity (0-1)
)
```

Available Ollama models:
- `llama3.2:3b` - Fast, efficient (recommended)
- `mistral:7b` - Good balance
- `qwen2.5:7b` - Strong reasoning
- `llama3.1:8b` - Larger, more capable

### Adding RAG (Vector Search)

The project already includes vector search implementation! To customize:

#### 1. Modify Vector Store

Edit `src/support_agent/vector_store.py`:

```python
# Use different embedding model
def __init__(self, embeddings_model: str = "sentence-transformers/all-mpnet-base-v2"):
```

Popular alternatives:
- `all-mpnet-base-v2` - Higher quality, slower
- `all-MiniLM-L12-v2` - Balance between speed and quality

#### 2. Test Vector Search

```bash
python scripts/init_vector_store.py
```

### Integrating Real Systems

#### Connect to Order Management System

```python
@tool
def get_order_status(order_id: str) -> str:
    """Look up real order status."""
    import requests
    
    response = requests.get(
        f"https://your-api.com/orders/{order_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    order = response.json()
    return format_order_status(order)
```

#### Connect to CRM

```python
@tool
def get_customer_info(email: str) -> str:
    """Get customer details from CRM."""
    # Connect to Salesforce, HubSpot, etc.
    customer = crm_client.get_customer(email)
    return format_customer_info(customer)
```

### Adding Conversation Memory

LangGraph already includes checkpointing, but you can extend it:

```python
# In agent.py
from langgraph.checkpoint.postgres import PostgresSaver

# Use PostgreSQL instead of SQLite
memory = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/dbname"
)
```

### Creating a Web UI

#### Simple React Frontend

```jsx
// Example: chat.jsx
import { useState } from 'react';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    const response = await fetch('http://localhost:8123/threads/my-thread/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: { messages: [{ role: 'user', content: input }] }
      })
    });
    
    const data = await response.json();
    setMessages([...messages, data.output.messages[-1]]);
  };
  
  return (
    <div>
      {messages.map(msg => <div>{msg.content}</div>)}
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

## 🧪 Testing

### Unit Tests

```python
# tests/test_tools.py
from src.support_agent.tools import get_order_status

def test_get_order_status():
    result = get_order_status("123456")
    assert "in_transit" in result.lower()
```

### Integration Tests

```python
# tests/test_graph.py
from src.support_agent import graph
from langchain_core.messages import HumanMessage

def test_full_conversation():
    result = graph.invoke({
        "messages": [HumanMessage(content="Check order #123456")]
    })
    assert len(result["messages"]) > 1
```

### Running Tests

```bash
# Run test conversations
python scripts/test_bot.py

# Test vector store
python scripts/init_vector_store.py

# Add your own tests in scripts/test_bot.py
```

## 🐳 Docker Option

If you prefer Docker:

```bash
docker-compose up
```

This starts both the bot and Ollama in containers.

## 🆘 Troubleshooting

### Installation Issues

#### Python Version Error

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

#### ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'langgraph'`

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Import Error from 'src'

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

### Ollama Issues

#### Ollama Not Running

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

#### Model Not Found

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

#### Ollama Running but Not Responding

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

### LangGraph Dev Issues

#### Port Already in Use

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

#### Graph Not Found

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

#### Changes Not Reflecting

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

### Runtime Issues

#### Agent Not Using Tools

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

#### Slow Responses

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

#### Memory/State Issues

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

#### Tool Execution Errors

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

### API Issues

#### API Returns 404

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

#### API Returns 500

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

#### Streaming Not Working

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

### Docker Issues

#### Container Won't Start

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

#### Can't Connect to Ollama in Docker

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

## 🔍 Vector Store Implementation

The knowledge base uses semantic vector search for intelligent document retrieval.

### How It Works

1. **Document Creation**: JSON knowledge base is converted into LangChain `Document` objects with:
   - `page_content`: The actual text content
   - `metadata`: Category tags for filtering (return, shipping, payment, product, general)

2. **Embedding Generation**: Each document is converted to a vector embedding using the `sentence-transformers/all-MiniLM-L6-v2` model

3. **Vector Search**: User queries are:
   - Converted to embeddings
   - Compared to all document embeddings using cosine similarity
   - Top-k most similar documents are returned
   - Optional category filtering narrows results

### Benefits

- **Semantic Understanding**: Finds relevant results even when exact keywords don't match
- **Better User Experience**: More intelligent responses to customer queries
- **Flexibility**: Easy to add new documents without restructuring code
- **Performance**: In-memory storage provides fast lookups
- **Scalability**: Can easily swap to persistent vector stores (ChromaDB, Pinecone, etc.) for production

### Usage

```python
# General search (all categories)
results = vector_store.search("Can I get a refund?", k=3)

# Category-specific search
results = vector_store.search("shipping options", k=2, filter_category="shipping")
```

### Testing Vector Store

```bash
python scripts/init_vector_store.py
```

## Development

### Hot Reload

LangGraph Dev automatically reloads when you change code. Just save your files and test immediately.

### Debugging

Use LangGraph Studio to:
- Set breakpoints on nodes
- Step through execution
- Inspect state at any point
- Time-travel debug (rewind and replay)

### Code Style

We use:
- **Black** for formatting: `black src/`
- **Ruff** for linting: `ruff check src/`
- **Type hints** where possible

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

## Common Patterns

### Adding Sentiment Analysis

```python
@tool
def analyze_sentiment(message: str) -> str:
    """Detect customer emotion."""
    # Use a sentiment model
    from transformers import pipeline
    sentiment = pipeline("sentiment-analysis")
    result = sentiment(message)[0]
    
    if result['label'] == 'NEGATIVE' and result['score'] > 0.8:
        return "customer_frustrated"
    return "neutral"
```

### Multi-step Workflows

```python
# For complex workflows, add conditional logic in agent.py
def should_follow_up(state: SupportState) -> str:
    last_msg = state["messages"][-1]
    if "thank" in last_msg.content.lower():
        return "end"
    return "continue"
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Update documentation
6. Submit pull request

## Getting Help

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

## Resources

- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [Tool Calling Guide](https://python.langchain.com/docs/modules/agents/tools/)
- [Ollama Models](https://ollama.ai/library)

## Next Steps

- [ ] Add RAG with vector database (ChromaDB) - ✅ Already implemented!
- [ ] Integrate with real order management system
- [ ] Add sentiment analysis for escalation
- [ ] Create web UI with React
- [ ] Add authentication and user management

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions:
- Check the [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- Open an issue on GitHub
- Review example conversations in `scripts/test_bot.py`

---

**Quick Command Reference:**

```bash
# Run visually
langgraph dev

# Run in terminal
python scripts/cli.py

# Run tests
python scripts/test_bot.py

# View examples
python scripts/api_client_example.py

# Test vector store
python scripts/init_vector_store.py

# Install deps
pip install -r requirements.txt

# Get Ollama model
ollama pull llama3.2:3b
```

Happy coding! 🚀