#!/bin/sh
set -e

echo "=========================================="
echo "Initializing Ollama with required models"
echo "=========================================="

# Set Ollama host
export OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
max_retries=30
retry_count=0

# Check if Ollama is ready using curl or ollama command
until (curl -s "$OLLAMA_HOST/api/tags" >/dev/null 2>&1 || ollama list >/dev/null 2>&1); do
    retry_count=$((retry_count + 1))
    if [ $retry_count -gt $max_retries ]; then
        echo "ERROR: Ollama service did not become ready in time"
        exit 1
    fi
    echo "Waiting for Ollama... (attempt $retry_count/$max_retries)"
    sleep 2
done

echo "✓ Ollama service is ready"

# Pull the required model
MODEL_NAME="${OLLAMA_MODEL:-llama3.1:latest}"
echo ""
echo "Pulling model: $MODEL_NAME"
echo "This may take a few minutes on first run..."

if ollama pull "$MODEL_NAME"; then
    echo "✓ Model $MODEL_NAME pulled successfully"
else
    echo "ERROR: Failed to pull model $MODEL_NAME"
    exit 1
fi

# Verify the model is available
echo ""
echo "Verifying model availability..."
if ollama list | grep -q "$MODEL_NAME"; then
    echo "✓ Model $MODEL_NAME is available and ready to use"
else
    echo "ERROR: Model $MODEL_NAME not found after pulling"
    exit 1
fi

echo ""
echo "=========================================="
echo "Ollama initialization complete!"
echo "Model: $MODEL_NAME"
echo "=========================================="
