#!/bin/bash
# Quick script to run LangSmith evaluations

set -e  # Exit on error

echo "========================================================================"
echo "LangSmith Evaluation Runner"
echo "========================================================================"
echo ""

# Check if API key is set
if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "❌ ERROR: LANGCHAIN_API_KEY not set"
    echo ""
    echo "Get your API key from: https://smith.langchain.com/settings"
    echo "Then run: export LANGCHAIN_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

echo "✅ LANGCHAIN_API_KEY is set"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating .venv..."
    echo ""

    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ ERROR: .venv not found. Please create it first:"
        echo "   python -m venv .venv"
        echo "   source .venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
else
    echo "✅ Virtual environment is activated"
fi

echo ""
echo "========================================================================"
echo "Running Setup Checker"
echo "========================================================================"
echo ""

python check_langsmith_setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Setup check failed. Please fix issues above."
    exit 1
fi

echo ""
echo "========================================================================"
echo "Running Evaluation"
echo "========================================================================"
echo ""

python -m src.support_agent.tests.eval_langsmith

echo ""
echo "========================================================================"
echo "Done!"
echo "========================================================================"
echo ""
echo "View your results online at: https://smith.langchain.com/projects"
echo "Search for: support-agent-eval"
echo ""
