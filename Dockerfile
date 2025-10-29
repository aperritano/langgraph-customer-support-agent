FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir langgraph-cli

# Copy project files
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose LangGraph Dev port
EXPOSE 8123

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run LangGraph Dev server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]
