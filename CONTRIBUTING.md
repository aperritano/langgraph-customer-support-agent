# Contributing to Customer Support Bot

Thank you for your interest in improving the customer support bot! This guide will help you add features and customize the bot.

## Adding a New Tool

Tools are how the agent interacts with external systems. Here's how to add one:

### 1. Define the Tool

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

### 2. Add to Tools List

At the bottom of `tools.py`:

```python
tools = [
    search_knowledge_base,
    get_order_status,
    # ... existing tools
    your_new_tool,  # Add here
]
```

### 3. Test It

```python
python scripts/test_bot.py
```

That's it! The agent will automatically learn to use your tool.

## Modifying the System Prompt

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

## Changing the LLM Model

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

## Adding RAG (Vector Search)

To add semantic search over your knowledge base:

### 1. Install Dependencies

```bash
pip install chromadb sentence-transformers
```

### 2. Create Vector Store

```python
# src/support_agent/vectorstore.py
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma(
    collection_name="support_kb",
    embedding_function=embeddings,
    persist_directory="./storage/chroma"
)
```

### 3. Add as Tool

```python
@tool
def semantic_search(query: str) -> str:
    """Search knowledge base using semantic similarity."""
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])
```

## Integrating Real Systems

### Connect to Order Management System

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

### Connect to CRM

```python
@tool
def get_customer_info(email: str) -> str:
    """Get customer details from CRM."""
    # Connect to Salesforce, HubSpot, etc.
    customer = crm_client.get_customer(email)
    return format_customer_info(customer)
```

## Adding Conversation Memory

LangGraph already includes checkpointing, but you can extend it:

```python
# In agent.py
from langgraph.checkpoint.postgres import PostgresSaver

# Use PostgreSQL instead of SQLite
memory = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/dbname"
)
```

## Creating a Web UI

### Simple React Frontend

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

## Testing

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

## Code Style

We use:
- **Black** for formatting: `black src/`
- **Ruff** for linting: `ruff check src/`
- **Type hints** where possible

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Update documentation
6. Submit pull request

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

## Getting Help

- Read the [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- Check existing issues
- Ask in discussions
- Review the example code

## Resources

- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [Tool Calling Guide](https://python.langchain.com/docs/modules/agents/tools/)
- [Ollama Models](https://ollama.ai/library)

Happy coding! 🚀
