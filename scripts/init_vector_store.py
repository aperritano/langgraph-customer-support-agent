#!/usr/bin/env python3
"""Script to initialize and test the knowledge base vector store."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.support_agent.vector_store import KnowledgeBaseVectorStore


def main():
    """Initialize vector store and run test queries."""
    print("🚀 Initializing Knowledge Base Vector Store\n")

    # Create vector store
    vector_store = KnowledgeBaseVectorStore()

    # Load knowledge base
    kb_path = Path(__file__).parent.parent / "data" / "knowledge_base.json"
    print(f"📁 Loading knowledge base from: {kb_path}\n")
    vector_store.load_from_json(str(kb_path))

    print("\n" + "="*60)
    print("Testing Vector Store with Sample Queries")
    print("="*60 + "\n")

    # Test queries
    test_queries = [
        ("What is your return policy?", "return"),
        ("How long does shipping take?", "shipping"),
        ("What payment methods do you accept?", "payment"),
        ("Tell me about the wireless headphones", "product"),
        ("What are your business hours?", "general"),
        ("Can I get a refund?", None),  # No category filter
    ]

    for query, category in test_queries:
        print(f"🔍 Query: {query}")
        if category:
            print(f"   Category filter: {category}")

        results = vector_store.search(query, k=2, filter_category=category)
        print(f"\n📄 Results:\n{results}")
        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    main()
