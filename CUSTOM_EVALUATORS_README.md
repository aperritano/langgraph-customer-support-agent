# Custom Evaluators - Complete System

## ✅ What Was Created

A comprehensive custom evaluator system with **7 ready-to-use evaluators** plus a framework for creating your own.

### Files Created

1. **[custom_evaluators.py](src/support_agent/tests/custom_evaluators.py)** - 7 production-ready evaluators
2. **[CUSTOM_EVALUATORS_GUIDE.md](src/support_agent/tests/CUSTOM_EVALUATORS_GUIDE.md)** - Complete documentation
3. **[eval_langsmith.py](src/support_agent/tests/eval_langsmith.py)** - Updated to use custom evaluators

## 🎯 Available Evaluators

### Currently Active (5 evaluators)
1. ✅ **Tool Usage** - Checks if correct tool was called
2. ✅ **Keyword Presence** - Verifies expected info in response
3. ✅ **Response Quality** - Checks completeness and formatting
4. ✅ **Empathy** - Detects empathetic language in difficult situations
5. ✅ **Actionability** - Ensures response provides clear next steps

### Ready to Activate (2 more)
6. **Politeness** - Checks for courtesy and professional tone
7. **Conciseness** - Evaluates appropriate response length
8. **Specificity** - Prefers specific details over generic statements
9. **Tool Efficiency** - Checks for efficient tool usage
10. **Resolution Clarity** - Ensures clear problem resolution

## 🚀 Quick Start

### View Current Evaluators

Run the evaluation to see all 5 active evaluators:

```bash
python -m src.support_agent.tests.eval_langsmith
```

Output shows:
```
Preparing Evaluators
======================================================================

  - Tool Usage Checker
  - Keyword Presence Checker
  - Response Quality Checker
  - Empathy Checker           ← NEW!
  - Actionability Checker     ← NEW!
```

### Add More Evaluators

Edit [eval_langsmith.py](src/support_agent/tests/eval_langsmith.py) line 463:

```python
# Current (2 custom evaluators)
evaluators.extend([empathy_evaluator, actionability_evaluator])

# Add more (5 custom evaluators)
evaluators.extend([
    empathy_evaluator,
    actionability_evaluator,
    politeness_evaluator,      # NEW
    conciseness_evaluator,     # NEW
    specificity_evaluator,     # NEW
])

# Or use pre-defined groups
evaluators.extend(ALL_CUSTOM_EVALUATORS)  # All 7
```

### Use Evaluator Groups

```python
from src.support_agent.tests.custom_evaluators import (
    EMPATHY_EVALUATORS,      # empathy + politeness
    EFFICIENCY_EVALUATORS,   # conciseness + tool_efficiency
    COMPLETENESS_EVALUATORS, # actionability + specificity + resolution
)

evaluators.extend(EMPATHY_EVALUATORS)
```

## 📊 How to View Results

### Method 1: LangSmith Web Interface (Recommended)

1. Run evaluation
2. Click the link shown in output (or go to https://smith.langchain.com)
3. Find your experiment (search "support-agent-eval")
4. View:
   - **Aggregate scores** - Average for each evaluator
   - **Per-example results** - Scores for each test case
   - **Feedback comments** - Why each test passed/failed
   - **Full traces** - Complete conversation flows

**Example what you'll see:**

```
Evaluator          | Avg Score | Tests Passed
-------------------|-----------|-------------
tool_usage         | 100%      | 10/10
keyword_presence   | 85%       | 8/10
response_quality   | 100%      | 10/10
empathy            | 80%       | 8/10
actionability      | 95%       | 9/10
```

Click any test to see detailed feedback:

```
Test #6: "I want to return order #123456 because it's defective"

✅ tool_usage (100%)
   "Correctly used initiate_return"

✅ keyword_presence (100%)
   "All keywords present: return, authorization, RMA, free"

✅ response_quality (100%)
   "Good response quality (87 words)"

✅ empathy (100%)
   "Shows empathy: apologize, inconvenience"

✅ actionability (100%)
   "Highly actionable: includes next_steps, timeframes, clear_info"
```

### Method 2: Terminal Output

The terminal shows:
- Number of evaluators run
- Link to detailed results
- Instructions for viewing online

Note: Detailed scores appear in LangSmith, not terminal (by design).

## 🎨 Evaluator Examples

### 1. Empathy Evaluator

**What it does**: Checks if agent shows empathy when customers are frustrated

**Example Pass**:
```
Customer: "This is ridiculous! I've been waiting for weeks!"
Agent: "I completely understand your frustration, and I sincerely apologize
       for the inconvenience. Let me help you resolve this right away."

✅ empathy (100%) - Shows empathy: understand, apologize
```

**Example Fail**:
```
Customer: "This is ridiculous! I've been waiting for weeks!"
Agent: "Your order status is: in transit. Expected delivery: Oct 31."

❌ empathy (0%) - No empathetic language detected for negative situation
```

### 2. Actionability Evaluator

**What it does**: Checks if response provides clear, actionable next steps

**Example Pass**:
```
Agent: "You can track your order at: https://track.example.com/1Z999
       Expected delivery: Oct 31, 2025
       Tracking number: 1Z999AA10123456784"

✅ actionability (100%) - Highly actionable: includes links, timeframes, clear_info
```

**Example Fail**:
```
Agent: "Your order is being processed and will ship soon."

❌ actionability (30%) - Response lacks actionable information or next steps
```

## 🛠️ Create Your Own Evaluator

### Template

```python
from langsmith.schemas import Run, Example

def my_evaluator(run: Run, example: Example) -> dict:
    """Description of what this checks."""
    response = run.outputs.get("answer", "")

    # Your logic here
    if some_condition:
        return {
            "key": "my_metric",
            "score": 1.0,
            "comment": "Why it passed"
        }
    else:
        return {
            "key": "my_metric",
            "score": 0.0,
            "comment": "Why it failed"
        }
```

### Example: Check for Discount Mention

```python
def discount_mention_evaluator(run: Run, example: Example) -> dict:
    """Check if agent mentions available discounts."""
    response = run.outputs.get("answer", "").lower()
    question = example.inputs.get("question", "").lower()

    # Only apply to pricing questions
    if "price" not in question and "cost" not in question:
        return {"key": "discount_mention", "score": 1.0, "comment": "N/A"}

    discount_words = ["discount", "promo", "coupon", "sale", "special offer"]
    has_discount = any(word in response for word in discount_words)

    return {
        "key": "discount_mention",
        "score": 1.0 if has_discount else 0.5,
        "comment": "Mentions discounts" if has_discount else "Could mention available discounts"
    }
```

Add to your evaluators:

```python
evaluators.append(discount_mention_evaluator)
```

## 📈 Best Practices

### 1. Start with Core Evaluators
Begin with 3-5 evaluators:
```python
evaluators = [
    tool_usage_evaluator,       # Did agent call right tool?
    keyword_presence_evaluator, # Does response have key info?
    empathy_evaluator,          # Is agent empathetic?
]
```

### 2. Add Based on Your Priorities

**Focus on customer satisfaction?**
```python
evaluators.extend([empathy_evaluator, politeness_evaluator])
```

**Focus on efficiency?**
```python
evaluators.extend([conciseness_evaluator, tool_efficiency_evaluator])
```

**Focus on completeness?**
```python
evaluators.extend([actionability_evaluator, specificity_evaluator])
```

### 3. Track Improvements

Run regularly and track trends:

```
Week 1: empathy=75%, actionability=80%
Week 2: empathy=85%, actionability=90%  ✅ Improving!
Week 3: empathy=70%, actionability=88%  ⚠️  Regression
```

### 4. Set Quality Gates

```python
# After running evaluation, check in LangSmith:
# If any metric < 80%, investigate and improve
```

## 📚 Documentation

- **[CUSTOM_EVALUATORS_GUIDE.md](src/support_agent/tests/CUSTOM_EVALUATORS_GUIDE.md)** - Complete guide
- **[custom_evaluators.py](src/support_agent/tests/custom_evaluators.py)** - Source code with 7 evaluators
- **[eval_langsmith.py](src/support_agent/tests/eval_langsmith.py)** - Main evaluation script

## ✅ Status

**Currently Active**: 5 evaluators (3 core + 2 custom)

**Available to Add**: 5 more custom evaluators

**Results**: View at https://smith.langchain.com/projects

**Working**: ✅ Tested and verified

## 🎉 Summary

You now have:

✅ **7 production-ready custom evaluators**
- Empathy
- Politeness
- Actionability
- Specificity
- Conciseness
- Tool Efficiency
- Resolution Clarity

✅ **2 currently active** (empathy + actionability)

✅ **Framework for creating your own**

✅ **Complete documentation**

✅ **Integration with LangSmith dashboard**

✅ **Tested and working**

**The evaluators are ready to use - results show up in LangSmith after each evaluation run!**

---

**Next Steps:**

1. Run evaluation: `python -m src.support_agent.tests.eval_langsmith`
2. View results in LangSmith (link shown in output)
3. Review scores for each evaluator
4. Add more evaluators as needed
5. Track improvements over time
