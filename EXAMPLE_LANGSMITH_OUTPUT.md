# Example LangSmith Output

This document shows what you'll see when you run the evaluation script and view results in LangSmith.

## Terminal Output

```
======================================================================
CUSTOMER SUPPORT AGENT EVALUATION
======================================================================
Timestamp: 2025-10-29 14:30:00
Dataset: customer-support-qa
Experiment: support-agent-eval
======================================================================

======================================================================
Creating dataset: customer-support-qa
======================================================================

Created dataset: a1b2c3d4-5678-90ab-cdef-1234567890ab

Adding test cases:
  [ 1] return_policy        | What's your return policy?
  [ 2] shipping             | Do you offer international shipping?
  [ 3] payment              | What payment methods do you accept?
  [ 4] order_status         | Can you check the status of order #123456?
  [ 5] order_status         | Where is my order 789012?
  [ 6] return_request       | I want to return order #123456 because it's defective
  [ 7] inventory            | Is the wireless mouse in stock?
  [ 8] inventory            | Do you have any laptops available?
  [ 9] complex              | Hi! I ordered a keyboard last week but haven't received it yet. Can you help?
  [10] escalation           | This is ridiculous! I've been waiting for weeks and nobody can help me!

Dataset created with 10 examples
View at: https://smith.langchain.com/datasets/a1b2c3d4-5678-90ab-cdef-1234567890ab

======================================================================
Preparing Evaluators
======================================================================

  - Tool Usage Checker
  - Keyword Presence Checker
  - Response Quality Checker

======================================================================
Running Evaluation
======================================================================

[Processing examples 1-10...]

======================================================================
EVALUATION COMPLETE!
======================================================================

Results Summary:
  - Experiment: support-agent-eval-a1b2c3d4
  - Total Examples: 10

Average Scores:
  - tool_usage          : 90.00%
  - keyword_presence    : 85.00%
  - response_quality    : 100.00%

======================================================================
VIEW RESULTS ONLINE
======================================================================

Dataset:
  https://smith.langchain.com/datasets/a1b2c3d4-5678-90ab-cdef-1234567890ab

Experiment Results:
  https://smith.langchain.com/projects

Search for: support-agent-eval

======================================================================
```

## What Shows Up in LangSmith Web Interface

### 1. Dataset View (`https://smith.langchain.com/datasets/...`)

You'll see a table with all your test cases:

| Example | Input | Expected Output |
|---------|-------|-----------------|
| 1 | "What's your return policy?" | should_mention: ["30 days", "return", "refund"]<br>should_use_tool: "search_vector_knowledge_base" |
| 2 | "Do you offer international shipping?" | should_mention: ["shipping", "international"]<br>should_use_tool: "search_vector_knowledge_base" |
| 3 | "What payment methods do you accept?" | should_mention: ["payment", "credit card"]<br>should_use_tool: "search_vector_knowledge_base" |
| ... | ... | ... |

### 2. Experiment View (`https://smith.langchain.com/projects`)

**Overall Metrics Dashboard:**
```
Experiment: support-agent-eval-a1b2c3d4
Date: Oct 29, 2025 2:30 PM
Examples: 10

Metrics:
┌────────────────────┬────────┬────────┬────────┐
│ Metric             │ Avg    │ Min    │ Max    │
├────────────────────┼────────┼────────┼────────┤
│ tool_usage         │ 90.0%  │ 0.0%   │ 100%   │
│ keyword_presence   │ 85.0%  │ 66.7%  │ 100%   │
│ response_quality   │ 100%   │ 100%   │ 100%   │
└────────────────────┴────────┴────────┴────────┘
```

**Per-Example Results:**

| # | Input | tool_usage | keyword_presence | response_quality | Status |
|---|-------|------------|------------------|------------------|--------|
| 1 | "What's your return policy?" | ✅ 100% | ✅ 100% | ✅ 100% | Pass |
| 2 | "Do you offer international shipping?" | ✅ 100% | ⚠️ 66.7% | ✅ 100% | Partial |
| 3 | "What payment methods do you accept?" | ✅ 100% | ✅ 100% | ✅ 100% | Pass |
| 4 | "Can you check the status of order #123456?" | ✅ 100% | ✅ 100% | ✅ 100% | Pass |
| ... | ... | ... | ... | ... | ... |

### 3. Individual Trace View (Click any example)

```
Example #4: "Can you check the status of order #123456?"

┌─ Agent Execution ────────────────────────────────────────────┐
│                                                               │
│  [1] Agent Node                                               │
│      Input: "Can you check the status of order #123456?"     │
│      Decision: Call get_order_status                          │
│      Duration: 1.2s                                           │
│                                                               │
│  [2] Tool Node                                                │
│      Tool: get_order_status                                   │
│      Args: {"order_id": "123456"}                             │
│      Result: "📦 Order #123456 - In Transit..."              │
│      Duration: 0.1s                                           │
│                                                               │
│  [3] Agent Node                                               │
│      Input: [Previous messages + tool result]                 │
│      Decision: Respond to user                                │
│      Output: "Your order is on its way! Expected..."         │
│      Duration: 1.5s                                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─ Evaluation Results ──────────────────────────────────────────┐
│                                                               │
│  ✅ tool_usage (100%)                                         │
│     Correctly used get_order_status                           │
│                                                               │
│  ✅ keyword_presence (100%)                                   │
│     All keywords present: in transit, tracking                │
│                                                               │
│  ✅ response_quality (100%)                                   │
│     Good response quality (45 words)                          │
│                                                               │
└───────────────────────────────────────────────────────────────┘

Full Agent Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your order is on its way! It's currently in transit and expected
to arrive by Oct 31, 2025. You can track it using tracking number
1Z999AA10123456784 at: https://track.example.com/1Z999AA10123456784

Your order includes:
- Wireless Headphones
- USB Cable

Let me know if you need anything else!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Failed Example (Example #2 - Partial Pass)

```
Example #2: "Do you offer international shipping?"

┌─ Evaluation Results ──────────────────────────────────────────┐
│                                                               │
│  ✅ tool_usage (100%)                                         │
│     Correctly used search_vector_knowledge_base               │
│                                                               │
│  ⚠️  keyword_presence (66.7%)                                 │
│     Partial match. Missing: international                     │
│                                                               │
│  ✅ response_quality (100%)                                   │
│     Good response quality (38 words)                          │
│                                                               │
└───────────────────────────────────────────────────────────────┘

Issues to Fix:
- Response mentioned "shipping" but didn't explicitly say "international"
- Consider improving prompt to ensure key terms are included in response
```

## How to Use These Results

### 1. Identify Patterns
- Which types of questions fail most?
- Which evaluators have lowest scores?
- Are certain tools not being called when expected?

### 2. Iterate on Prompts
Based on failures, improve your system prompt in `prompts.py`:

```python
# Before
SYSTEM_PROMPT = "You are a helpful assistant..."

# After (based on eval results)
SYSTEM_PROMPT = """You are a helpful assistant...

When answering customer questions:
- Always include key terms from their question in your response
- Explicitly confirm the specific details they asked about
- Use concrete examples when possible
"""
```

### 3. Add More Test Cases
When you find edge cases, add them to the dataset:

```python
{
    "inputs": {"question": "Edge case you discovered"},
    "outputs": {
        "should_mention": ["expected", "keywords"],
        "should_use_tool": "expected_tool"
    }
}
```

### 4. Track Improvement Over Time
Run evaluations after each change:

```bash
# Version 1 - Baseline
python -m src.support_agent.tests.eval_langsmith
# Results: 85% average

# Version 2 - After prompt improvement
python -m src.support_agent.tests.eval_langsmith
# Results: 92% average

# Version 3 - After tool improvements
python -m src.support_agent.tests.eval_langsmith
# Results: 97% average
```

LangSmith will track all runs and let you compare them side-by-side.

### 5. Set Quality Gates
Use scores to decide if changes are ready to deploy:

```python
# In CI/CD pipeline
if average_score >= 0.90:
    print("✅ Quality gate passed - safe to deploy")
else:
    print("❌ Quality gate failed - needs improvement")
    sys.exit(1)
```

## Next Steps

1. Run the evaluation: `python -m src.support_agent.tests.eval_langsmith`
2. Review results in LangSmith web interface
3. Identify lowest-scoring examples
4. Make improvements to agent
5. Re-run to measure improvement
6. Repeat until satisfied with performance

## Tips for Success

- **Start small**: 10 test cases is enough to get started
- **Focus on failures**: Learn more from failures than successes
- **Iterate quickly**: Run evals after every change
- **Add edge cases**: When users report issues, add them to dataset
- **Track trends**: Use experiment names to organize runs over time
