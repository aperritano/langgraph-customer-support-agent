# 🎉 You've Downloaded: Customer Support Bot

## What You Have

A complete, production-ready customer support agent built with:
- ✅ LangGraph for orchestration
- ✅ Local LLM via Ollama (privacy-first)
- ✅ 5 pre-built tools (order tracking, returns, KB search, etc.)
- ✅ Visual debugging with LangGraph Studio
- ✅ REST API ready to use
- ✅ Full documentation and examples

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

## 📁 What's Inside

```
customer-support-bot/
├── 📄 README.md              ← Start here for full docs
├── 📄 QUICKSTART.md          ← 5-minute setup guide
├── 📄 PROJECT_STRUCTURE.md   ← Understand the code
├── 📄 CONTRIBUTING.md        ← Learn to extend it
├── 📄 TROUBLESHOOTING.md     ← Fix common issues
│
├── src/support_agent/        ← Main application code
│   ├── agent.py             ← Graph definition (THE CORE)
│   ├── tools.py             ← 5 support tools
│   ├── state.py             ← State management
│   └── prompts.py           ← System instructions
│
├── scripts/                  ← Ready-to-run scripts
│   ├── cli.py               ← Interactive chat
│   ├── test_bot.py          ← Automated tests
│   └── api_client_example.py ← API usage examples
│
├── data/                     ← Knowledge base
│   └── knowledge_base.json
│
└── Config files (langgraph.json, requirements.txt, etc.)
```

## 🎯 Try These First

Once running, try these example queries:

1. "What's your return policy?"
2. "Can you check order #123456?"
3. "I want to return my order because it's defective"
4. "Do you have laptops in stock?"
5. "This is terrible service!" (watch it escalate!)

## 📚 Documentation Guide

- **Just want it running?** → Read `QUICKSTART.md`
- **Want to understand it?** → Read `PROJECT_STRUCTURE.md`
- **Want to customize it?** → Read `CONTRIBUTING.md`
- **Something broken?** → Read `TROUBLESHOOTING.md`
- **Full details?** → Read `README.md`

## 🔧 Quick Customization

### Change the LLM Model
Edit `src/support_agent/agent.py`:
```python
llm = ChatOllama(model="mistral:7b")  # Change this line
```

### Modify Agent Behavior
Edit `src/support_agent/prompts.py`:
```python
SYSTEM_PROMPT = """Your custom instructions here..."""
```

### Add New Tools
Edit `src/support_agent/tools.py`:
```python
@tool
def my_new_tool(param: str) -> str:
    """What it does."""
    return "result"

tools = [..., my_new_tool]  # Add to list
```

## 🐳 Docker Option

If you prefer Docker:
```bash
docker-compose up
```

This starts both the bot and Ollama in containers.

## 🆘 Need Help?

**Bot won't start?**
- Check: Is Ollama running? (`ollama list`)
- Check: Is Python 3.11+? (`python --version`)
- See: `TROUBLESHOOTING.md`

**Model errors?**
```bash
ollama pull llama3.2:3b
```

**Port already in use?**
```bash
langgraph dev --port 8124
```

**Still stuck?**
Read `TROUBLESHOOTING.md` for detailed solutions.

## 🎓 Learning Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Ollama Models](https://ollama.ai/library)
- Check the `scripts/` folder for working examples

## ✨ What Makes This Special

1. **Runs Locally** - No API keys needed, full privacy
2. **Production Ready** - Real error handling, memory, logging
3. **Visual Debugging** - LangGraph Studio built-in
4. **Easy to Extend** - Add tools in minutes
5. **Well Documented** - Every file explained
6. **Real Examples** - Working code for every feature

## 🚀 Next Steps

1. ✅ Run `langgraph dev`
2. ✅ Open http://127.0.0.1:8123
3. ✅ Try example queries
4. ✅ Read `CONTRIBUTING.md` to customize
5. ✅ Build something awesome!

## 📞 Questions?

- Check the docs in this folder
- All code is commented
- Examples in `scripts/`
- Troubleshooting guide included

**Now go build something amazing!** 🎉

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

# Install deps
pip install -r requirements.txt

# Get Ollama model
ollama pull llama3.2:3b
```

Happy coding! 🚀
