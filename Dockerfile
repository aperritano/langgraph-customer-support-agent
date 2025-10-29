FROM python:3.12.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "langgraph-cli[inmem]"

# Copy project files
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose LangGraph Dev port
EXPOSE 8123

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_BASE_URL=http://ollama:11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8123/health || exit 1

# Run LangGraph Dev server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]
