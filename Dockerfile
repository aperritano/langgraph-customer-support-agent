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
EXPOSE 2024

# Set environment variables
ENV PYTHONUNBUFFERED=1
# OLLAMA_BASE_URL should be set via docker-compose.yml or .env file
# Defaults to http://localhost:11434 in agent.py if not set

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:2024/ || exit 1

# Run LangGraph Dev server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]
