# LangSmith Evaluation Guide

Complete guide to running evaluations that show up in the LangSmith web interface.

## Quick Start

### 1. Setup LangSmith

Get your API key from https://smith.langchain.com/settings and set it:

```bash
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT="customer-support-eval"
```

### 2. Install Dependencies

```bash
source .venv/bin/activate
pip install langsmith
```

### 3. Run Evaluation

```bash
python -m src.support_agent.tests.eval_langsmith
```

## What Gets Created

### Dataset: "customer-support-qa"
10 test cases covering:
- Return policy questions
- Order status checks
- Product availability
- Return requests
- Escalation scenarios

### Evaluators (3 metrics)
1. **Tool Usage** - Did agent call the right tool?
2. **Keyword Presence** - Does response contain expected info?
3. **Response Quality** - Is response complete and well-formed?

### Results in LangSmith
- View dataset with all test cases
- View experiment with scores per example
- View detailed traces for each run
- Compare experiments over time

## Expected Output

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

Created dataset: abc123

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
View at: https://smith.langchain.com/datasets/abc123

======================================================================
Preparing Evaluators
======================================================================

  - Tool Usage Checker
  - Keyword Presence Checker
  - Response Quality Checker

======================================================================
Running Evaluation
======================================================================

Progress: 10/10 examples processed...

======================================================================
EVALUATION COMPLETE!
======================================================================

Results Summary:
  - Experiment: support-agent-eval-20251029-143000
  - Total Examples: 10

Average Scores:
  - tool_usage          : 90.00%
  - keyword_presence    : 85.00%
  - response_quality    : 100.00%

======================================================================
VIEW RESULTS ONLINE
======================================================================

Dataset:
  https://smith.langchain.com/datasets/abc123

Experiment Results:
  https://smith.langchain.com/projects

Search for: support-agent-eval

======================================================================
```

## Viewing Results Online

### 1. View Dataset
Click the dataset link to see all test cases with inputs and expected outputs.

### 2. View Experiment
Go to Projects > Search "support-agent-eval" to see:
- Overall scores
- Per-example results
- Failed examples
- Detailed traces

### 3. View Individual Traces
Click any example to see:
- Full conversation flow
- Tool calls made
- LLM inputs/outputs
- Evaluation scores

### 4. Compare Runs
Run the evaluation multiple times to:
- Track improvements over time
- A/B test different prompts
- Compare different models

## Customizing Evaluations

### Add More Test Cases

Edit the `test_cases` list in [eval_langsmith.py](eval_langsmith.py):

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

### Add LLM-as-Judge Evaluators

Uncomment this line in the script:

```python
evaluators.extend(create_llm_evaluators())
```

This adds GPT-4 based evaluators for:
- Helpfulness
- Professionalism

Note: This uses OpenAI API and costs money per evaluation.

### Create Custom Evaluators

Add your own evaluator function:

```python
def my_custom_evaluator(run: Run, example: Example) -> dict:
    response = run.outputs.get("answer", "")

    # Your evaluation logic here
    score = 1.0 if "something" in response else 0.0

    return {
        "key": "my_metric",
        "score": score,
        "comment": "Your feedback here"
    }

# Add to evaluators list
evaluators.append(my_custom_evaluator)
```

## Tips

### Running Faster
Increase concurrency in the evaluate() call:

```python
results = evaluate(
    run_support_agent,
    data=DATASET_NAME,
    evaluators=evaluators,
    max_concurrency=4,  # Run 4 examples in parallel
)
```

### Debugging Failures
If an example fails, check:
1. The trace in LangSmith (shows full conversation)
2. The evaluation feedback (shows why it failed)
3. The tools_used output (shows which tools were called)

### Best Practices
1. Start with a small dataset (10 examples)
2. Use simple evaluators first
3. Add LLM evaluators once basic tests pass
4. Run regularly to catch regressions
5. Use experiment_prefix to organize runs

## Troubleshooting

### Error: "LANGCHAIN_API_KEY not set"
```bash
export LANGCHAIN_API_KEY="your-key-here"
```

### Error: "Dataset already exists"
The script automatically deletes and recreates the dataset. If you see errors, manually delete it in the UI first.

### Agent takes too long
Reduce the dataset size or increase max_concurrency for faster evaluation.

### Scores are low
This is expected on the first run! Use the results to:
1. Identify which examples fail
2. Improve prompts or tools
3. Re-run to see improvement

## Next Steps

After running your first evaluation:

1. Review failed examples in LangSmith
2. Improve your agent based on feedback
3. Re-run evaluation to measure improvement
4. Add more test cases for edge cases
5. Set up CI/CD to run evals automatically

## Resources

- LangSmith Docs: https://docs.smith.langchain.com/
- Evaluation Guide: https://docs.smith.langchain.com/evaluation
- Example Code: [eval_langsmith.py](eval_langsmith.py)
