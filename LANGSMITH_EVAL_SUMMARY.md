# LangSmith Evaluation System - Summary

## Overview

A complete evaluation framework for the customer support agent that automatically tests responses against 10 diverse customer scenarios and scores them using 5 automated evaluators. The system creates a dataset, runs the agent against each test case, evaluates responses for tool usage, keyword presence, response quality, empathy, and actionability, then uploads detailed results with full conversation traces to the LangSmith dashboard at https://smith.langchain.com. Results include aggregate scores, per-test feedback explaining why tests passed or failed, and complete execution traces for debugging. Run with `python -m src.support_agent.tests.eval_langsmith` to execute evaluations, then view detailed metrics and trends in the LangSmith web interface to track improvements over time and catch regressions.

## Quick Start

```bash
# Setup
export LANGCHAIN_API_KEY="your-key-here"

# Run
python -m src.support_agent.tests.eval_langsmith

# View results at:
https://smith.langchain.com/projects
```

## Files

- **eval_langsmith.py** - Main evaluation script (10 test cases, 5 evaluators)
- **custom_evaluators.py** - 7 additional evaluators (empathy, politeness, etc.)
- **check_langsmith_setup.py** - Setup validation tool

## Features

- ✅ 10 test cases covering returns, orders, inventory, escalations
- ✅ 5 active evaluators (3 core + 2 custom: empathy & actionability)
- ✅ 7 additional evaluators available (politeness, conciseness, etc.)
- ✅ Online dashboard with detailed traces and feedback
- ✅ Track improvements and compare runs over time
- ✅ Production-ready and tested

**View results in LangSmith Experiments tab (not Evaluators tab) after running evaluation.**
