# Project Structure Overview

Complete file structure and description of the Customer Support Bot project.

## 📁 Root Directory

```
customer-support-bot/
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick setup guide
├── CONTRIBUTING.md           # Developer guide for extending the bot
├── TROUBLESHOOTING.md        # Common issues and solutions
├── LICENSE                   # MIT License
├── langgraph.json           # LangGraph configuration (required)
├── pyproject.toml           # Python project metadata
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── Dockerfile              # Container configuration
└── docker-compose.yml      # Multi-container setup
```

## 📁 src/support_agent/ - Main Application

```
src/support_agent/
├── __init__.py             # Package initialization
├── agent.py               # 🎯 MAIN: Graph definition and entry point
├── state.py              # State schema (TypedDict)
├── tools.py              # Tool implementations (@tool decorators)
└── prompts.py            # System prompts for the agent
```

### Key Files

**agent.py** - The heart of the application
- Defines the LangGraph workflow
- Creates agent and tool nodes
- Implements ReAct loop (reasoning + acting)
- Exports `graph` variable for LangGraph Dev

**tools.py** - Business logic
- `search_knowledge_base()` - Find policies and FAQ
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

## 📁 scripts/ - Utilities

```
scripts/
├── cli.py                    # Interactive command-line interface
├── test_bot.py              # Automated test suite
└── api_client_example.py    # API usage examples
```

### Scripts Usage

**cli.py** - Chat with the bot interactively
```bash
python scripts/cli.py
```

**test_bot.py** - Run test conversations
```bash
python scripts/test_bot.py
```

**api_client_example.py** - Learn API usage
```bash
python scripts/api_client_example.py
```

## 📁 data/ - Knowledge Base

```
data/
└── knowledge_base.json      # Mock KB data (policies, FAQ, products)
```

Contains:
- Store policies (returns, shipping, warranty)
- Product information
- FAQ answers
- Order status definitions

## 📁 storage/ - Generated at Runtime

```
storage/                     # Created automatically
└── checkpoints.db          # SQLite database for conversation memory
```

This directory is created when you first run the bot. It stores:
- Conversation history
- Agent state checkpoints
- Session data

## 📦 Configuration Files

### langgraph.json
Maps the graph name to the Python code location. Required by LangGraph Dev.

```json
{
  "graphs": {
    "support_agent": "./src/support_agent/agent.py:graph"
  }
}
```

### pyproject.toml
Python project metadata and dependencies using modern packaging standards.

### requirements.txt
Simple pip-compatible dependency list for easy installation.

### .env.example
Template for environment variables. Copy to `.env` and customize:
```bash
cp .env.example .env
```

## 🐳 Docker Files

### Dockerfile
Builds a container image with:
- Python 3.11
- All dependencies
- LangGraph CLI
- Exposes port 8123

### docker-compose.yml
Orchestrates two services:
- `support-bot` - The LangGraph application
- `ollama` - Local LLM server

## 📚 Documentation Files

### README.md
- Features overview
- Installation instructions
- Usage examples
- Configuration guide

### QUICKSTART.md
- 5-minute setup guide
- Common commands
- Quick troubleshooting

### CONTRIBUTING.md
- How to add tools
- Modifying the system prompt
- Integrating real systems
- Testing patterns

### TROUBLESHOOTING.md
- Installation issues
- Ollama problems
- Runtime errors
- Performance optimization

## 🔍 File Size Reference

Approximate file sizes:

| Category | Files | Total Lines |
|----------|-------|-------------|
| Core Code | 5 | ~600 |
| Scripts | 3 | ~600 |
| Docs | 5 | ~800 |
| Config | 6 | ~100 |
| **Total** | **19** | **~2100** |

## 🎯 Entry Points

There are multiple ways to run the bot:

1. **LangGraph Studio** (Visual UI)
   - Entry: `langgraph dev`
   - Uses: `langgraph.json` → `agent.py:graph`

2. **Command Line** (Interactive)
   - Entry: `python scripts/cli.py`
   - Uses: `src/support_agent/`

3. **Test Suite** (Automated)
   - Entry: `python scripts/test_bot.py`
   - Uses: `src/support_agent/`

4. **API Client** (Programmatic)
   - Entry: `python scripts/api_client_example.py`
   - Uses: LangGraph Dev API

5. **Direct Test** (Quick check)
   - Entry: `python -m src.support_agent.agent`
   - Uses: `agent.py` main block

## 🔧 Customization Points

To customize the bot, edit:

1. **Behavior** → `src/support_agent/prompts.py`
2. **Tools** → `src/support_agent/tools.py`
3. **State** → `src/support_agent/state.py`
4. **Flow** → `src/support_agent/agent.py`
5. **Data** → `data/knowledge_base.json`
6. **Model** → `src/support_agent/agent.py` (LLM config)

## 📊 Dependencies

Core dependencies (see requirements.txt):
- `langgraph` - Graph orchestration framework
- `langchain-core` - Core LangChain functionality
- `langchain-ollama` - Ollama LLM integration
- `langchain-community` - Community tools

Runtime requirements:
- Python 3.11+
- Ollama (for local LLM)
- SQLite (built into Python)

## 🚀 Deployment Options

1. **Local Development**
   - Run: `langgraph dev`
   - Best for: Testing and development

2. **Docker Local**
   - Run: `docker-compose up`
   - Best for: Consistent environments

3. **LangGraph Cloud**
   - Run: `langgraph deploy`
   - Best for: Production deployment

4. **Custom Server**
   - Use: Gunicorn/Uvicorn
   - Best for: Custom infrastructure

## 📝 Notes

- All code is well-commented
- Type hints throughout for IDE support
- Follows modern Python best practices
- Async-ready for future scaling
- Modular design for easy extension

## 🎓 Learning Path

Recommended order to understand the codebase:

1. Read `README.md` - Overview
2. Read `QUICKSTART.md` - Get it running
3. Explore `tools.py` - See what it can do
4. Read `agent.py` - Understand the flow
5. Try `cli.py` - Interact with it
6. Read `CONTRIBUTING.md` - Learn to extend it
7. Check `test_bot.py` - See examples

## 📞 Support

- Questions? → Check `TROUBLESHOOTING.md`
- Want to contribute? → Read `CONTRIBUTING.md`
- Found a bug? → Create an issue
- Need help? → Review documentation

Happy coding! 🚀
