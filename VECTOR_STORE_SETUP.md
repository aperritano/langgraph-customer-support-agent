# Vector Store Implementation

This document describes the vector store implementation for the knowledge base.

## Overview

The knowledge base has been converted from a simple dictionary-based lookup to a **semantic vector search** using LangChain's `InMemoryVectorStore` and HuggingFace embeddings. This enables more intelligent and relevant search results based on semantic meaning rather than exact keyword matches.

## Components

### 1. Vector Store Module
**File**: [src/support_agent/vector_store.py](src/support_agent/vector_store.py)

This module provides:
- `KnowledgeBaseVectorStore` class: Manages embedding creation and vector search
- `get_vector_store()` function: Singleton accessor for the global vector store instance
- Automatic loading from [data/knowledge_base.json](data/knowledge_base.json)

### 2. Updated Dependencies
**File**: [requirements.txt](requirements.txt)

Added:
- `sentence-transformers>=2.2.2` - For creating text embeddings
- Uses `langchain-huggingface` for the embeddings interface

### 3. Updated Tool
**File**: [src/support_agent/tools.py](src/support_agent/tools.py:40-69)

The `search_knowledge_base` tool now:
- Uses vector similarity search instead of category-based dictionary lookup
- Returns top-k most semantically relevant results
- Supports category filtering for more targeted searches

### 4. Test Script
**File**: [scripts/init_vector_store.py](scripts/init_vector_store.py)

Demonstrates vector store functionality with sample queries across different categories.

## How It Works

1. **Document Creation**: JSON knowledge base is converted into LangChain `Document` objects with:
   - `page_content`: The actual text content
   - `metadata`: Category tags for filtering (return, shipping, payment, product, general)

2. **Embedding Generation**: Each document is converted to a vector embedding using the `sentence-transformers/all-MiniLM-L6-v2` model

3. **Vector Search**: User queries are:
   - Converted to embeddings
   - Compared to all document embeddings using cosine similarity
   - Top-k most similar documents are returned
   - Optional category filtering narrows results

## Benefits

- **Semantic Understanding**: Finds relevant results even when exact keywords don't match
- **Better User Experience**: More intelligent responses to customer queries
- **Flexibility**: Easy to add new documents without restructuring code
- **Performance**: In-memory storage provides fast lookups
- **Scalability**: Can easily swap to persistent vector stores (ChromaDB, Pinecone, etc.) for production

## Usage

### Basic Usage (Automatic)
The vector store is automatically initialized when the agent starts:

```python
from src.support_agent.vector_store import get_vector_store

vector_store = get_vector_store()  # Loads data/knowledge_base.json automatically
```

### Manual Testing
Run the test script to see vector search in action:

```bash
source .venv/bin/activate
python scripts/init_vector_store.py
```

### Search Examples
```python
# General search (all categories)
results = vector_store.search("Can I get a refund?", k=3)

# Category-specific search
results = vector_store.search("shipping options", k=2, filter_category="shipping")
```

## Expanding the Knowledge Base

To add new information:

1. Edit [data/knowledge_base.json](data/knowledge_base.json)
2. Restart the agent - vector store auto-reloads
3. Or manually reload: `vector_store.load_from_json("path/to/knowledge_base.json")`

## Model Configuration

The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`:
- Fast and efficient
- 384-dimensional embeddings
- Good quality for most use cases

To use a different model, modify [vector_store.py](src/support_agent/vector_store.py:14):

```python
def __init__(self, embeddings_model: str = "sentence-transformers/all-mpnet-base-v2"):
```

Popular alternatives:
- `all-mpnet-base-v2` - Higher quality, slower
- `all-MiniLM-L12-v2` - Balance between speed and quality

## Production Considerations

For production deployment, consider:

1. **Persistent Storage**: Use ChromaDB, Pinecone, or Weaviate instead of InMemoryVectorStore
2. **Caching**: Cache embeddings to avoid recomputation
3. **Batch Processing**: Generate embeddings for large datasets in batches
4. **Monitoring**: Track search quality and relevance metrics
5. **Updates**: Implement incremental updates for knowledge base changes

## Testing

The implementation has been tested with various queries:

✅ Return policy queries
✅ Shipping information
✅ Payment methods
✅ Product information
✅ General FAQ
✅ Cross-category queries

All tests return semantically relevant results.
