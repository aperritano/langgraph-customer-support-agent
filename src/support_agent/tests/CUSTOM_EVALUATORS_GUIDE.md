# Custom Evaluators Guide

This guide explains how to use and create custom evaluators for your LangSmith evaluations.

## What Are Custom Evaluators?

Custom evaluators are Python functions that automatically score your agent's responses based on specific criteria. They help you measure qualities beyond just correctness, such as:

- **Empathy**: Does the agent show understanding in difficult situations?
- **Politeness**: Is the response courteous and professional?
- **Actionability**: Does the response provide clear next steps?
- **Conciseness**: Is the response appropriately brief?
- **Tool Efficiency**: Did the agent use tools efficiently?

## Available Custom Evaluators

The [custom_evaluators.py](custom_evaluators.py) file includes 7 ready-to-use evaluators:

### 1. Empathy Evaluator
**What it checks**: Does the agent show empathy when customers are frustrated?

**Looks for**: "I understand", "I apologize", "I'm sorry", "Let me help"

**Example**:
- Input: "This is ridiculous! I've been waiting for weeks!"
- Pass: "I completely understand your frustration, and I apologize..."
- Fail: "Your order status is..."

### 2. Politeness Evaluator
**What it checks**: Is the response polite and professional?

**Looks for**: Greetings, "please", "thank you", offers to help further

**Score**: 0-100% based on presence of courtesy indicators

### 3. Actionability Evaluator
**What it checks**: Does the response provide clear, actionable information?

**Looks for**: Next steps, links, instructions, timeframes, specific details

**Example**:
- Good: "You can track your order at: https://... Expected delivery: Oct 31"
- Poor: "Your order will arrive soon"

### 4. Specificity Evaluator
**What it checks**: Is the response specific rather than generic?

**Looks for**: Dates, numbers, order IDs, tracking numbers, concrete details

**Penalizes**: Generic phrases like "as soon as possible", "shortly"

### 5. Conciseness Evaluator
**What it checks**: Is the response appropriately concise?

**Optimal**: 30-150 words

**Penalizes**: Too short (<30 words) or too verbose (>200 words)

### 6. Tool Efficiency Evaluator
**What it checks**: Did the agent use tools efficiently?

**Looks for**:
- Appropriate number of tool calls
- No redundant calls
- Right tools for the task

### 7. Resolution Clarity Evaluator
**What it checks**: Does the response clearly resolve the issue?

**Looks for**: Direct answer, resolution statement, follow-up offer

## How to Use Custom Evaluators

### Method 1: Use Pre-configured Groups

Edit [eval_langsmith.py](eval_langsmith.py):

```python
from src.support_agent.tests.custom_evaluators import (
    EMPATHY_EVALUATORS,      # empathy + politeness
    EFFICIENCY_EVALUATORS,   # conciseness + tool_efficiency
    COMPLETENESS_EVALUATORS, # actionability + specificity + resolution_clarity
)

# In run_evaluation() function:
evaluators = [
    tool_usage_evaluator,
    keyword_presence_evaluator,
    response_quality_evaluator,
]

# Add custom evaluator groups
evaluators.extend(EMPATHY_EVALUATORS)
evaluators.extend(EFFICIENCY_EVALUATORS)
```

### Method 2: Pick Individual Evaluators

```python
from src.support_agent.tests.custom_evaluators import (
    empathy_evaluator,
    actionability_evaluator,
    conciseness_evaluator,
)

evaluators = [
    tool_usage_evaluator,
    keyword_presence_evaluator,
    response_quality_evaluator,
    empathy_evaluator,        # Add individual evaluator
    actionability_evaluator,  # Add another
]
```

### Method 3: Use All Custom Evaluators

```python
from src.support_agent.tests.custom_evaluators import ALL_CUSTOM_EVALUATORS

evaluators = [
    tool_usage_evaluator,
    keyword_presence_evaluator,
    response_quality_evaluator,
]
evaluators.extend(ALL_CUSTOM_EVALUATORS)  # Add all 7 custom evaluators
```

## Current Setup

The evaluation script is **already configured** to use 2 custom evaluators:
- ✅ Empathy Evaluator
- ✅ Actionability Evaluator

To add more, edit lines 449-464 in [eval_langsmith.py](eval_langsmith.py).

## Creating Your Own Evaluator

Here's a template for creating a custom evaluator:

```python
from langsmith.schemas import Run, Example

def my_custom_evaluator(run: Run, example: Example) -> dict:
    """
    Description of what this evaluator checks.
    """
    # Get the agent's response
    response = run.outputs.get("answer", "")

    # Get the customer's question (optional)
    question = example.inputs.get("question", "")

    # Your evaluation logic here
    # Return a score between 0.0 and 1.0

    if some_condition:
        return {
            "key": "my_metric",          # Unique identifier
            "score": 1.0,                # 0.0 to 1.0
            "comment": "Why it passed"   # Feedback message
        }
    else:
        return {
            "key": "my_metric",
            "score": 0.0,
            "comment": "Why it failed"
        }
```

### Example: Check for Greeting

```python
def greeting_evaluator(run: Run, example: Example) -> dict:
    """Check if agent includes a greeting."""
    response = run.outputs.get("answer", "").lower()

    greetings = ["hi", "hello", "welcome", "good morning", "good afternoon"]
    has_greeting = any(g in response for g in greetings)

    if has_greeting:
        return {
            "key": "has_greeting",
            "score": 1.0,
            "comment": "Includes friendly greeting"
        }
    else:
        return {
            "key": "has_greeting",
            "score": 0.0,
            "comment": "No greeting found"
        }
```

Then add it to your evaluators list:

```python
evaluators = [
    tool_usage_evaluator,
    greeting_evaluator,  # Your new evaluator
]
```

## Viewing Evaluator Results

### In LangSmith Web Interface

After running the evaluation, go to https://smith.langchain.com and you'll see:

1. **Aggregate View**: Average scores for each evaluator across all tests
   ```
   Evaluator          | Avg Score | Pass Rate
   -------------------|-----------|----------
   tool_usage         | 90%       | 9/10
   keyword_presence   | 85%       | 8/10
   empathy            | 75%       | 7/10
   actionability      | 95%       | 10/10
   ```

2. **Per-Example View**: Click any test to see:
   - Individual scores for each evaluator
   - Feedback comments explaining the score
   - Full conversation trace
   - Tool calls made

3. **Comparison View**: Compare different evaluation runs to track improvements

### In Terminal

The script will show:
```
======================================================================
EVALUATION COMPLETE!
======================================================================

Results Summary:
  - Total Examples: 10
  - Evaluators Run: 5

======================================================================
EVALUATION SCORES
======================================================================

Scores are being calculated in LangSmith...
View detailed metrics in the web interface (link below)
```

Note: Detailed scores appear in LangSmith, not the terminal. This is by design - the web interface provides much richer visualizations.

## Best Practices

### 1. Start Simple
Begin with 3-5 evaluators. Too many can be overwhelming.

```python
# Good starting set
evaluators = [
    tool_usage_evaluator,
    keyword_presence_evaluator,
    empathy_evaluator,
]
```

### 2. Match Your Priorities
Choose evaluators that align with your quality goals:

- **Customer satisfaction focused**: Use empathy + politeness + resolution_clarity
- **Efficiency focused**: Use conciseness + tool_efficiency
- **Completeness focused**: Use actionability + specificity

### 3. Iterate Based on Results
1. Run evaluation
2. Review low-scoring examples in LangSmith
3. Improve agent (prompts, tools, etc.)
4. Re-run to measure improvement

### 4. Set Thresholds
Decide minimum acceptable scores:

```python
# After running evaluation, check results
if empathy_score < 0.80:
    print("⚠️  Empathy needs improvement")
if actionability_score < 0.90:
    print("⚠️  Need more actionable responses")
```

### 5. Track Trends
Run evaluations regularly to track improvement:

```
Week 1: empathy=75%, actionability=80%
Week 2: empathy=85%, actionability=90%  ✅ Improving!
Week 3: empathy=70%, actionability=88%  ⚠️  Regression in empathy
```

## Example: Full Setup

Here's a complete example of using custom evaluators:

```python
# In eval_langsmith.py

from src.support_agent.tests.custom_evaluators import (
    empathy_evaluator,
    politeness_evaluator,
    actionability_evaluator,
    conciseness_evaluator,
)

def run_evaluation():
    # ... existing code ...

    # Configure evaluators
    evaluators = [
        # Core evaluators (always include these)
        tool_usage_evaluator,
        keyword_presence_evaluator,
        response_quality_evaluator,

        # Custom evaluators for customer satisfaction
        empathy_evaluator,
        politeness_evaluator,

        # Custom evaluators for response quality
        actionability_evaluator,
        conciseness_evaluator,
    ]

    # Run evaluation
    results = evaluate(
        run_support_agent,
        data=DATASET_NAME,
        evaluators=evaluators,
        experiment_prefix="support-agent-v2",  # Version your experiments
    )
```

## Troubleshooting

### Issue: Evaluators not showing in results
**Solution**: Check LangSmith web interface - scores appear there, not in terminal

### Issue: All scores are 0 or 1 (no nuance)
**Solution**: Adjust your evaluator logic to return gradual scores (0.5, 0.7, etc.)

### Issue: Evaluator is too strict/lenient
**Solution**: Adjust the thresholds in your evaluator logic

### Issue: Want to test evaluator before running full evaluation
**Solution**: Create a test file:

```python
from langsmith.schemas import Run, Example
from custom_evaluators import empathy_evaluator

# Mock data
test_run = Run(outputs={"answer": "I apologize for the inconvenience..."})
test_example = Example(inputs={"question": "This is ridiculous!"})

# Test evaluator
result = empathy_evaluator(test_run, test_example)
print(f"Score: {result['score']}")
print(f"Comment: {result['comment']}")
```

## Next Steps

1. **Review current results**: Run evaluation and check LangSmith
2. **Choose evaluators**: Pick 2-3 custom evaluators that match your goals
3. **Add to eval script**: Edit [eval_langsmith.py](eval_langsmith.py)
4. **Re-run evaluation**: See new metrics in LangSmith
5. **Iterate**: Improve agent based on scores

## Summary

Custom evaluators let you:
- ✅ Measure subjective qualities automatically
- ✅ Track improvements over time
- ✅ Set quality standards
- ✅ Catch regressions
- ✅ Focus improvement efforts

**The custom evaluators are ready to use - just uncomment the ones you want in eval_langsmith.py!**
