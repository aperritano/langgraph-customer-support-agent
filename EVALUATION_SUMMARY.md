# LangSmith Evaluation - Quick Summary

## What I Created

A complete, production-ready evaluation system for your customer support agent that shows results in the LangSmith web interface.

## Files Created

1. **[eval_langsmith.py](src/support_agent/tests/eval_langsmith.py)** - Main evaluation script
   - Creates dataset with 10 test cases
   - Runs agent against each test
   - Evaluates with 3 metrics
   - Uploads results to LangSmith

2. **[LANGSMITH_EVAL_GUIDE.md](src/support_agent/tests/LANGSMITH_EVAL_GUIDE.md)** - Complete documentation
   - Setup instructions
   - Detailed explanation of evaluators
   - Customization guide
   - Troubleshooting

3. **[EXAMPLE_LANGSMITH_OUTPUT.md](EXAMPLE_LANGSMITH_OUTPUT.md)** - Example output
   - Shows terminal output
   - Shows web interface screenshots (text)
   - Explains how to use results

4. **[check_langsmith_setup.py](check_langsmith_setup.py)** - Setup checker
   - Validates environment variables
   - Checks dependencies
   - Tests LangSmith connection

5. **Updated [README.md](README.md)** - Added evaluation section

## How to Run

### Step 1: Get LangSmith API Key

Go to https://smith.langchain.com/settings and copy your API key.

### Step 2: Configure

```bash
export LANGCHAIN_API_KEY="lsv2_pt_your_key_here"
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT="customer-support-eval"
```

### Step 3: Verify Setup

```bash
python check_langsmith_setup.py
```

Expected output:
```
======================================================================
LANGSMITH EVALUATION SETUP CHECKER
======================================================================

Checking environment variables...
  ✅ LANGCHAIN_API_KEY is set (lsv2_pt_...)
  ✅ LANGCHAIN_TRACING_V2=true (traces enabled)
  ✅ LANGCHAIN_PROJECT=customer-support-eval

Checking dependencies...
  ✅ langsmith            - LangSmith client
  ✅ langgraph            - LangGraph framework
  ✅ langchain_core       - LangChain core

Testing LangSmith connection...
  ✅ Successfully connected to LangSmith

Checking agent setup...
  ✅ Agent graph imported successfully

======================================================================
SUMMARY
======================================================================
  ✅ PASS     Environment
  ✅ PASS     Dependencies
  ✅ PASS     LangSmith Connection
  ✅ PASS     Agent

🎉 All checks passed! You're ready to run evaluations.

Run the evaluation:
  python -m src.support_agent.tests.eval_langsmith
```

### Step 4: Run Evaluation

```bash
python -m src.support_agent.tests.eval_langsmith
```

## What Shows Up Online

### 1. Dataset
https://smith.langchain.com/datasets

You'll see "customer-support-qa" with 10 test cases:

| Example | Category | Question |
|---------|----------|----------|
| 1 | return_policy | What's your return policy? |
| 2 | shipping | Do you offer international shipping? |
| 3 | payment | What payment methods do you accept? |
| 4 | order_status | Can you check the status of order #123456? |
| 5 | order_status | Where is my order 789012? |
| 6 | return_request | I want to return order #123456 because it's defective |
| 7 | inventory | Is the wireless mouse in stock? |
| 8 | inventory | Do you have any laptops available? |
| 9 | complex | Hi! I ordered a keyboard last week... |
| 10 | escalation | This is ridiculous! I've been waiting for weeks... |

### 2. Experiment Results
https://smith.langchain.com/projects

Search for "support-agent-eval" to see:

**Metrics:**
- **tool_usage** (90%): Did agent call the right tool?
- **keyword_presence** (85%): Does response contain expected info?
- **response_quality** (100%): Is response complete and well-formed?

**Per-Example Results:**
- Click any example to see full trace
- See which evaluators passed/failed
- View detailed feedback

### 3. Traces
Click any example to see:
- Full conversation flow
- Tool calls made
- LLM inputs/outputs
- Evaluation scores
- Feedback comments

## The Three Evaluators

### 1. Tool Usage Evaluator
**What it checks**: Did the agent call the expected tool?

Example:
- Input: "Can you check order #123456?"
- Expected tool: `get_order_status`
- Score: 100% if tool was called, 0% if not

### 2. Keyword Presence Evaluator
**What it checks**: Does the response mention expected keywords?

Example:
- Input: "What's your return policy?"
- Expected keywords: ["30 days", "return", "refund"]
- Score: % of keywords found in response

### 3. Response Quality Evaluator
**What it checks**: Is the response well-formed?

Checks:
- Not too short (>10 words)
- Not too long (<500 words)
- Ends with punctuation
- Score: 100% if all checks pass

## Customization

### Add Test Cases
Edit `test_cases` list in [eval_langsmith.py](src/support_agent/tests/eval_langsmith.py):

```python
test_cases.append({
    "inputs": {"question": "Your question here"},
    "outputs": {
        "should_mention": ["keyword1", "keyword2"],
        "should_use_tool": "tool_name",
        "category": "test_type"
    }
})
```

### Add Custom Evaluators
Create your own evaluator function:

```python
def my_evaluator(run: Run, example: Example) -> dict:
    response = run.outputs.get("answer", "")
    score = 1.0 if "something" in response else 0.0
    return {
        "key": "my_metric",
        "score": score,
        "comment": "Feedback here"
    }

evaluators.append(my_evaluator)
```

### Enable LLM-as-Judge
Uncomment this line in the script:

```python
evaluators.extend(create_llm_evaluators())
```

This adds GPT-4 evaluators for:
- Helpfulness
- Professionalism

**Note**: Uses OpenAI API (costs money)

## Benefits

### 1. Track Performance Over Time
Run evaluations after each change to measure improvement:

```
Version 1: 85% average → Version 2: 92% average → Version 3: 97% average
```

### 2. Catch Regressions
If scores drop after a change, you know something broke.

### 3. Identify Weak Spots
See which types of questions fail most often.

### 4. A/B Test Prompts
Compare different prompts or models side-by-side.

### 5. Quality Gates
Only deploy if scores meet threshold:

```python
if average_score >= 0.90:
    print("✅ Safe to deploy")
else:
    print("❌ Needs improvement")
```

## Next Steps

1. ✅ Run setup checker: `python check_langsmith_setup.py`
2. ✅ Run evaluation: `python -m src.support_agent.tests.eval_langsmith`
3. ✅ View results in LangSmith web interface
4. ✅ Review failed examples
5. ✅ Improve agent based on feedback
6. ✅ Re-run to measure improvement

## Resources

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Evaluation Guide**: https://docs.smith.langchain.com/evaluation
- **Your Code**: [eval_langsmith.py](src/support_agent/tests/eval_langsmith.py)
- **Full Guide**: [LANGSMITH_EVAL_GUIDE.md](src/support_agent/tests/LANGSMITH_EVAL_GUIDE.md)
- **Example Output**: [EXAMPLE_LANGSMITH_OUTPUT.md](EXAMPLE_LANGSMITH_OUTPUT.md)

## Support

If you have questions:
1. Check [LANGSMITH_EVAL_GUIDE.md](src/support_agent/tests/LANGSMITH_EVAL_GUIDE.md) for detailed docs
2. View [EXAMPLE_LANGSMITH_OUTPUT.md](EXAMPLE_LANGSMITH_OUTPUT.md) for expected output
3. Run `python check_langsmith_setup.py` to debug setup issues

---

**You now have a complete evaluation system that will show results online in LangSmith!**
