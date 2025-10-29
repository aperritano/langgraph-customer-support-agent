# Developer Setup - Native Ollama + Docker

## Overview

This setup uses **native Ollama** (running outside Docker) to leverage GPU acceleration (Metal on Apple Silicon, CUDA on NVIDIA), then runs the LangGraph agent in Docker for consistency and isolation.

**Why this approach?**

- ✅ **GPU Acceleration**: Native Ollama automatically uses Metal GPU (Apple Silicon) or CUDA (NVIDIA), providing 50-100x faster inference
- ✅ **Simple Setup**: No need to configure GPU passthrough in Docker
- ✅ **Consistent Environment**: Agent runs in Docker, avoiding local Python dependency conflicts
- ✅ **Hot Reload**: Code changes in `src/` automatically reload in the container

---

## Prerequisites

- **Docker Desktop** (macOS/Windows) or Docker (Linux) - **must be running**
- **Ollama** installed natively (not in Docker)
- **Python 3.12** (required for building the Docker image)

**Verify prerequisites:**

```bash
# Check Docker is running
docker --version
docker ps  # Should not error

# Check Python version
python3.12 --version  # Should show 3.12.x
```

---

## Step-by-Step Setup

### Step 1: Install Ollama Natively

**macOS:**

```bash
brew install ollama
```

**Linux:**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**

Download from [ollama.ai/download/windows](https://ollama.ai/download/windows)

**Verify installation:**

```bash
ollama --version
```

### Step 2: Start Ollama Service

**macOS/Linux:**

```bash
# Start Ollama in the background (or keep it running in a terminal)
ollama serve
```

**Windows:**

Ollama typically runs as a service automatically after installation.

**Verify it's running:**

```bash
curl http://localhost:11434/api/version
# Should return: {"version":"..."}
```

### Step 3: Pull the Required Model

Pull the `llama3.2:1b` model (recommended for fast CPU/GPU inference):

```bash
ollama pull llama3.2:1b
```

This will download ~1.3GB the first time. The model will be stored locally and reused.

**Verify the model:**

```bash
ollama list
# Should show: llama3.2:1b
```

### Step 4: Build Docker Image (One-Time)

Build the LangGraph agent Docker image:

**Create virtual environment (if it doesn't exist):**

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR: .venv\Scripts\activate  # Windows
```

**Build the Docker image:**

```bash
# Ensure virtual environment is activated (check prompt shows (.venv))
# Build with LangGraph CLI
langgraph build -t customer-support-bot:latest
```

This will:

- Pull the base LangGraph API image
- Install your project dependencies
- Create the Docker image tagged as `customer-support-bot:latest`
- Take 2-5 minutes on first build

**Note:** If you don't have `langgraph-cli` installed:

```bash
pip install langgraph-cli
```

### Step 5: Start the Docker Container

**Ensure Docker is running** (check Docker Desktop is started)

Start the LangGraph agent container (it will connect to your native Ollama):

```bash
docker-compose up
```

Or to run in detached mode (background):

```bash
docker-compose up -d
```

This will:

- ✅ Start the `support-bot` container
- ✅ Connect to native Ollama at `http://host.docker.internal:11434`
- ✅ Enable hot reload (edit `src/` files and see changes)
- ✅ Expose the agent at `http://localhost:8123`

### Step 6: Access the Application

**Wait for the server to start** (check logs show "Server started"):

```bash
docker-compose logs -f support-bot
# Look for: "Server started in X.XXs"
```

Open your browser and navigate to:

- **Agent UI / LangGraph Studio**: <http://localhost:8123>
- **API Documentation**: <http://localhost:8123/docs> (Swagger UI)
- **Native Ollama API**: <http://localhost:11434> (if you need to check status)

**Note:** The server logs will show a Studio URL like:

```plaintext
Studio UI: https://smith.langchain.com/studio/?baseUrl=http://0.0.0.0:8123
```

Use `http://localhost:8123` instead of `http://0.0.0.0:8123` when configuring (they're equivalent, but localhost is clearer).

### Step 7: Configure Agent UI with Graph URL

When you first access the Agent UI, you need to configure it to connect to your LangGraph server:

1. **Open Agent UI**: Go to <http://localhost:8123> in your browser

2. **Enter Graph Configuration**:

   - **Graph URL**: `http://localhost:8123`
   - **Graph Name**: `agent` (this matches the graph name in `langgraph.json`)
   - **API Key**: Leave empty (not needed for local development)

3. **Using LangGraph Studio (Recommended)**:

   The easiest way is to use the LangGraph Studio URL that appears in your server logs:

   ```plaintext
   https://smith.langchain.com/studio/?baseUrl=http://localhost:8123
   ```

   This automatically configures the Studio to connect to your local graph. You can also find this URL in the container logs:

   ```bash
   docker-compose logs support-bot | grep "Studio UI"
   ```

4. **Verify Connection**:

- You should see the chat interface
- The UI should show the graph name "agent" or ready status
- You can now start chatting with your customer support agent
- Try a test message: "Hello, what's your return policy?"

**Troubleshooting Connection**:

If the Agent UI can't connect:

- ✅ Ensure the Docker container is running: `docker-compose ps`
- ✅ Check the logs: `docker-compose logs support-bot`
- ✅ Verify the server is responding:

   ```bash
   curl http://localhost:8123/docs  # Should show Swagger UI HTML
   ```

- ✅ Check the Studio URL in logs:

   ```bash
   docker-compose logs support-bot | grep "Studio UI"
   ```

- ✅ Verify the graph is registered:

   ```bash
   docker-compose logs support-bot | grep "Registering graph"
   # Should show: Registering graph with id 'agent'
   ```

---

## Development Workflow

### Make Code Changes

1. **Edit code** in `src/support_agent/` - changes automatically reload
2. **Restart if needed:**

   ```bash
   docker-compose restart support-bot
   ```

### View Logs

```bash
# Follow logs
docker-compose logs -f support-bot

# Last 50 lines
docker-compose logs --tail 50 support-bot
```

### Stop Everything

```bash
docker-compose down
```

**Note:** Native Ollama keeps running in the background (as expected). If you want to stop it:

```bash
# Find and kill Ollama process
pkill ollama  # macOS/Linux
```

### Rebuild After Dependency Changes

If you modify `requirements.txt` or `pyproject.toml`:

```bash
# Rebuild the Docker image
langgraph build -t customer-support-bot:latest

# Restart containers
docker-compose restart support-bot
```

---

## Troubleshooting

### Ollama Not Found

**Error:** `Cannot connect to Ollama at http://host.docker.internal:11434`

**Solution:**

1. Verify Ollama is running:

   ```bash
   curl http://localhost:11434/api/version
   ```

2. Ensure Docker Desktop is running
3. On Linux, `host.docker.internal` might not work - use your host IP instead:

   ```bash
   # Find your host IP
   hostname -I | awk '{print $1}'
   # Update docker-compose.yml: OLLAMA_BASE_URL=http://<your-ip>:11434
   ```

### Model Not Found

**Error:** `model 'llama3.2:1b' not found`

**Solution:**

```bash
ollama pull llama3.2:1b
```

### Slow Performance

**On Apple Silicon (M1/M2/M3):**

- Native Ollama automatically uses Metal GPU - no configuration needed
- If it's slow, check Activity Monitor > GPU tab to verify GPU usage

**On NVIDIA GPUs:**

- Ensure CUDA drivers are installed
- Ollama should automatically detect and use the GPU

**On CPU-only systems:**

- `llama3.2:1b` is optimized for CPU inference
- Expect 5-30 second responses (still much better than larger models)

### Docker Container Can't Reach Ollama

**Check connectivity:**

```bash
docker exec langgraph-customer-support-agent-support-bot-1 curl http://host.docker.internal:11434/api/version
```

**Linux workaround:**

If `host.docker.internal` doesn't work on Linux, use your machine's IP:

```yaml
# In docker-compose.yml
environment:
  - OLLAMA_BASE_URL=http://192.168.1.XXX:11434  # Replace with your IP
```

---

## Configuration

### Using a Different Model

1. **Pull a different model:**

   ```bash
   ollama pull llama3.1:latest  # or mistral:7b, qwen2.5:7b, etc.
   ```

2. **Update the model in code:**

   Edit `src/support_agent/agent.py`:

   ```python
   llm = ChatOllama(
       model="llama3.1:latest",  # Change this
       # ... rest of config
   )
   ```

3. **Restart the container:**

   ```bash
   docker-compose restart support-bot
   ```

### Changing Ollama Port

If your native Ollama runs on a different port:

1. **Update docker-compose.yml:**

   ```yaml
   environment:
     - OLLAMA_BASE_URL=http://host.docker.internal:11435  # Custom port
   ```

2. **Restart:**

   ```bash
   docker-compose restart support-bot
   ```

---

## Quick Verification Checklist

After completing all steps, verify everything is working:

```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/version
# Expected: {"version":"..."}

# 2. Check model is available
ollama list | grep llama3.2:1b
# Expected: llama3.2:1b in the list

# 3. Check Docker container is running
docker-compose ps
# Expected: support-bot container shows "Up"

# 4. Check LangGraph server is responding
curl http://localhost:8123/docs
# Expected: HTML response (Swagger UI)

# 5. Check graph is registered
docker-compose logs support-bot | grep "Registering graph"
# Expected: "Registering graph with id 'agent'"

# 6. Test connectivity from container to Ollama
docker exec langgraph-customer-support-agent-support-bot-1 curl -s http://host.docker.internal:11434/api/version
# Expected: {"version":"..."}
```

If all checks pass, you're ready to use the Agent UI!

---

## Summary

✅ **Install Ollama natively** → Get GPU acceleration  
✅ **Pull `llama3.2:1b` model** → Fast, efficient inference  
✅ **Start native Ollama** → `ollama serve` (runs in background)  
✅ **Build Docker image** → `langgraph build -t customer-support-bot:latest`  
✅ **Start container** → `docker-compose up`  
✅ **Configure Agent UI** → Connect with graph URL `http://localhost:8123` and graph name `agent`  
✅ **Develop!** → Edit `src/`, changes auto-reload  

**Your agent is ready at:** <http://localhost:8123>
