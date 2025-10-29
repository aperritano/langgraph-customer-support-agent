#!/usr/bin/env python3
"""
Quick setup checker for LangSmith evaluations.

Run this before running the evaluation to ensure everything is configured correctly.

Usage: python scripts/check_langsmith_setup.py
"""

import os
import sys


def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")

    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("  ❌ LANGCHAIN_API_KEY not set")
        print("     Get your key from: https://smith.langchain.com/settings")
        print("     Then run: export LANGCHAIN_API_KEY='your-key-here'")
        return False
    else:
        print(f"  ✅ LANGCHAIN_API_KEY is set ({api_key[:10]}...)")

    tracing = os.getenv("LANGCHAIN_TRACING_V2")
    if tracing == "true":
        print("  ✅ LANGCHAIN_TRACING_V2=true (traces enabled)")
    else:
        print("  ⚠️  LANGCHAIN_TRACING_V2 not set (optional - set for detailed traces)")

    project = os.getenv("LANGCHAIN_PROJECT")
    if project:
        print(f"  ✅ LANGCHAIN_PROJECT={project}")
    else:
        print("  ⚠️  LANGCHAIN_PROJECT not set (optional - will use default)")

    return True


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")

    required = {
        "langsmith": "LangSmith client",
        "langgraph": "LangGraph framework",
        "langchain_core": "LangChain core",
    }

    all_installed = True
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✅ {package:20s} - {description}")
        except ImportError:
            print(f"  ❌ {package:20s} - {description} (NOT INSTALLED)")
            all_installed = False

    if not all_installed:
        print("\n  Install missing packages:")
        print("  pip install langsmith langgraph langchain-core")
        return False

    return True


def check_langsmith_connection():
    """Test connection to LangSmith."""
    print("\nTesting LangSmith connection...")

    try:
        from langsmith import Client
        client = Client()

        # Try to list datasets (should work if auth is valid)
        datasets = list(client.list_datasets(limit=1))
        print("  ✅ Successfully connected to LangSmith")
        return True

    except Exception as e:
        print(f"  ❌ Failed to connect to LangSmith: {e}")
        print("     Check your LANGCHAIN_API_KEY is valid")
        return False


def check_agent():
    """Check if the agent can be imported."""
    print("\nChecking agent setup...")

    try:
        from src.support_agent.agent import graph
        print("  ✅ Agent graph imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import agent: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 70)
    print("LANGSMITH EVALUATION SETUP CHECKER")
    print("=" * 70)
    print()

    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("LangSmith Connection", check_langsmith_connection),
        ("Agent", check_agent),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:10s} {name}")

    print()

    if all_passed:
        print("🎉 All checks passed! You're ready to run evaluations.")
        print()
        print("Run the evaluation:")
        print("  python -m src.support_agent.tests.eval_langsmith")
        print()
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Quick fixes:")
        print("  1. Set API key: export LANGCHAIN_API_KEY='your-key-here'")
        print("  2. Install deps: pip install langsmith")
        print("  3. Activate venv: source .venv/bin/activate")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
