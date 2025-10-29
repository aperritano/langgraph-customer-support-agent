#!/usr/bin/env python3
"""Script to initialize and test the knowledge base vector store.

WHAT THIS FILE DOES:
A utility script that loads the knowledge base into the vector store and tests
it with sample queries. Useful for debugging search issues or verifying the
knowledge base loaded correctly.

WHY IT'S IMPORTANT:
When search isn't working, it's helpful to have a standalone script to test
the vector store directly, without needing to run the full agent. Also useful
for verifying the knowledge base JSON file is formatted correctly.

Run: python scripts/init_vector_store.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.support_agent.vector_store import KnowledgeBaseVectorStore


def main():
    """
    Initialize vector store and run test queries.
    
    WHAT IT DOES:
    1. Creates a vector store instance
    2. Loads the knowledge_base.json file
    3. Runs several test queries to verify search works
    4. Displays results for manual inspection
    
    WHY IT'S IMPORTANT:
    Provides a quick way to verify the vector store is set up correctly and
    that searches are returning reasonable results.
    """
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
