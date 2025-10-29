# LangSmith Eval - Quick Start

Run evaluations in 3 steps:

## Step 1: Set API Key
```bash
export LANGCHAIN_API_KEY="lsv2_pt_your_key_here"
```
Get key: https://smith.langchain.com/settings

## Step 2: Check Setup
```bash
python check_langsmith_setup.py
```

## Step 3: Run Eval
```bash
python -m src.support_agent.tests.eval_langsmith
```

## View Results
https://smith.langchain.com/projects

Search for: **support-agent-eval**

---

## One-Command Alternative
```bash
export LANGCHAIN_API_KEY="your-key-here"
./run_eval.sh
```

---

## What You'll Get

**Dataset**: 10 test cases
- Return policy questions
- Order tracking
- Product availability
- Return requests
- Escalations

**Metrics**: 3 evaluators
- Tool usage (90%)
- Keyword presence (85%)
- Response quality (100%)

**Dashboard**: Online traces
- View each conversation
- See tool calls
- Review scores
- Track improvements

---

## Files

- [eval_langsmith.py](src/support_agent/tests/eval_langsmith.py) - Main script
- [LANGSMITH_EVAL_GUIDE.md](src/support_agent/tests/LANGSMITH_EVAL_GUIDE.md) - Full docs
- [EXAMPLE_LANGSMITH_OUTPUT.md](EXAMPLE_LANGSMITH_OUTPUT.md) - Example output
- [EVALUATION_SUMMARY.md](EVALUATION_SUMMARY.md) - Detailed summary

---

## Troubleshooting

**API key not set?**
```bash
export LANGCHAIN_API_KEY="your-key-here"
```

**Dependencies missing?**
```bash
source .venv/bin/activate
pip install langsmith
```

**Can't connect?**
```bash
python check_langsmith_setup.py
```

---

**That's it! Simple 3-step evaluation with online dashboard.**
