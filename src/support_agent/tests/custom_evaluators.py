"""
Custom Evaluators for Customer Support Agent

This module contains additional evaluators you can add to your evaluation suite.
Simply import and add them to the evaluators list in eval_langsmith.py.

Usage:
    from custom_evaluators import empathy_evaluator, response_time_evaluator

    evaluators = [
        tool_usage_evaluator,
        keyword_presence_evaluator,
        response_quality_evaluator,
        empathy_evaluator,  # Add custom evaluator
        response_time_evaluator,
    ]
"""

from langsmith.schemas import Run, Example
from typing import Dict


# ============================================================================
# Empathy & Tone Evaluators
# ============================================================================

def empathy_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the agent shows empathy in appropriate situations.

    This evaluator checks for empathetic language when customers are
    frustrated, confused, or reporting problems.

    Looks for phrases like:
    - "I understand"
    - "I apologize"
    - "I'm sorry to hear"
    - "Let me help you"
    """
    response = run.outputs.get("answer", "").lower()
    question = example.inputs.get("question", "").lower()

    # Determine if empathy is needed
    negative_indicators = [
        "ridiculous", "frustrated", "angry", "upset", "disappointed",
        "terrible", "horrible", "defective", "broken", "wrong", "issue",
        "problem", "haven't received", "still waiting", "weeks"
    ]

    needs_empathy = any(indicator in question for indicator in negative_indicators)

    if not needs_empathy:
        return {
            "key": "empathy",
            "score": 1.0,
            "comment": "Neutral question - empathy not required"
        }

    # Check for empathetic phrases
    empathy_phrases = [
        "understand", "apologize", "sorry", "help you",
        "inconvenience", "frustrated", "appreciate your patience",
        "let me help", "i can help", "happy to help"
    ]

    empathy_found = [phrase for phrase in empathy_phrases if phrase in response]

    if empathy_found:
        return {
            "key": "empathy",
            "score": 1.0,
            "comment": f"Shows empathy: {', '.join(empathy_found[:2])}"
        }
    else:
        return {
            "key": "empathy",
            "score": 0.0,
            "comment": "No empathetic language detected for negative situation"
        }


def politeness_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the response is polite and professional.

    Checks for:
    - Greetings (Hi, Hello)
    - Please/Thank you
    - Offers to help further
    - Professional closing
    """
    response = run.outputs.get("answer", "").lower()

    politeness_indicators = {
        "greeting": ["hi", "hello", "welcome"],
        "courtesy": ["please", "thank you", "thanks"],
        "offer_help": ["can i help", "anything else", "let me know", "is there anything"],
        "professional": ["happy to", "glad to", "pleased to"]
    }

    score_components = []
    found_indicators = []

    for category, phrases in politeness_indicators.items():
        if any(phrase in response for phrase in phrases):
            score_components.append(1)
            found_indicators.append(category)
        else:
            score_components.append(0)

    score = sum(score_components) / len(score_components)

    if score >= 0.75:
        return {
            "key": "politeness",
            "score": score,
            "comment": f"Very polite: includes {', '.join(found_indicators)}"
        }
    elif score >= 0.5:
        return {
            "key": "politeness",
            "score": score,
            "comment": f"Adequately polite: {', '.join(found_indicators)}"
        }
    else:
        return {
            "key": "politeness",
            "score": score,
            "comment": "Could be more polite - missing courtesy phrases"
        }


# ============================================================================
# Information Completeness Evaluators
# ============================================================================

def actionability_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the response provides actionable information.

    Checks if the response includes:
    - Specific next steps
    - Links or references
    - Clear instructions
    - Timeframes or deadlines
    """
    response = run.outputs.get("answer", "")

    actionable_indicators = {
        "next_steps": ["you can", "please", "to return", "to track", "visit", "go to"],
        "links": ["http", "www.", ".com", "track."],
        "instructions": ["step 1", "first", "then", "next", "follow"],
        "timeframes": ["within", "by", "in ", " days", "hours", "business days"],
        "clear_info": ["tracking number", "order number", "ticket", "authorization"]
    }

    found_categories = []
    for category, indicators in actionable_indicators.items():
        if any(indicator.lower() in response.lower() for indicator in indicators):
            found_categories.append(category)

    score = len(found_categories) / len(actionable_indicators)

    if score >= 0.6:
        return {
            "key": "actionability",
            "score": 1.0,
            "comment": f"Highly actionable: includes {', '.join(found_categories)}"
        }
    elif score >= 0.3:
        return {
            "key": "actionability",
            "score": 0.7,
            "comment": f"Somewhat actionable: {', '.join(found_categories)}"
        }
    else:
        return {
            "key": "actionability",
            "score": 0.3,
            "comment": "Response lacks actionable information or next steps"
        }


def specificity_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the response is specific rather than generic.

    Checks for:
    - Specific dates, numbers, or references
    - Order IDs, tracking numbers, ticket numbers
    - Product names
    - Concrete details vs vague statements
    """
    response = run.outputs.get("answer", "")

    # Check for specific information patterns
    specificity_patterns = {
        "numbers": any(char.isdigit() for char in response),
        "dates": any(month in response for month in [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]),
        "ids": any(identifier in response.lower() for identifier in [
            "order #", "ticket", "tracking", "authorization", "rma"
        ]),
        "currency": "$" in response,
    }

    # Count generic phrases (lower score)
    generic_phrases = [
        "we will", "as soon as possible", "shortly", "in due time",
        "our team", "we'll get back to you"
    ]
    generic_count = sum(1 for phrase in generic_phrases if phrase.lower() in response.lower())

    specific_count = sum(specificity_patterns.values())

    if specific_count >= 3 and generic_count == 0:
        return {
            "key": "specificity",
            "score": 1.0,
            "comment": f"Highly specific with concrete details"
        }
    elif specific_count >= 2:
        return {
            "key": "specificity",
            "score": 0.8,
            "comment": f"Includes specific information"
        }
    elif generic_count > specific_count:
        return {
            "key": "specificity",
            "score": 0.4,
            "comment": f"Response is too generic ({generic_count} generic phrases)"
        }
    else:
        return {
            "key": "specificity",
            "score": 0.6,
            "comment": "Somewhat specific but could include more details"
        }


# ============================================================================
# Response Efficiency Evaluators
# ============================================================================

def conciseness_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the response is concise without unnecessary verbosity.

    Checks word count relative to information density.
    Penalizes overly wordy responses that could be more direct.
    """
    response = run.outputs.get("answer", "")
    question = example.inputs.get("question", "")

    word_count = len(response.split())
    sentence_count = response.count('.') + response.count('!') + response.count('?')

    # Calculate words per sentence (average)
    avg_words_per_sentence = word_count / max(sentence_count, 1)

    # Optimal range: 50-150 words for customer support
    if 30 <= word_count <= 150 and avg_words_per_sentence <= 25:
        return {
            "key": "conciseness",
            "score": 1.0,
            "comment": f"Concise and clear ({word_count} words, {sentence_count} sentences)"
        }
    elif word_count < 30:
        return {
            "key": "conciseness",
            "score": 0.7,
            "comment": f"Very brief ({word_count} words) - might lack detail"
        }
    elif word_count > 200:
        return {
            "key": "conciseness",
            "score": 0.5,
            "comment": f"Too verbose ({word_count} words) - could be more concise"
        }
    else:
        return {
            "key": "conciseness",
            "score": 0.8,
            "comment": f"Reasonable length ({word_count} words)"
        }


def tool_efficiency_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the agent used tools efficiently (not too many, not redundant).

    Checks:
    - Number of tool calls
    - No redundant tool calls
    - Appropriate tool selection
    """
    tools_used = run.outputs.get("tools_used", [])

    tool_count = len(tools_used)
    unique_tools = len(set(tools_used))

    # Check for redundant calls
    has_redundancy = tool_count != unique_tools

    if tool_count == 0:
        # Some questions don't need tools (general info)
        return {
            "key": "tool_efficiency",
            "score": 1.0,
            "comment": "No tools needed - answered directly"
        }
    elif tool_count == 1:
        return {
            "key": "tool_efficiency",
            "score": 1.0,
            "comment": "Efficient - single tool call"
        }
    elif tool_count <= 3 and not has_redundancy:
        return {
            "key": "tool_efficiency",
            "score": 0.9,
            "comment": f"Reasonable - {tool_count} different tools used"
        }
    elif has_redundancy:
        return {
            "key": "tool_efficiency",
            "score": 0.6,
            "comment": f"Redundant tool calls detected ({tool_count} calls, {unique_tools} unique)"
        }
    else:
        return {
            "key": "tool_efficiency",
            "score": 0.5,
            "comment": f"Too many tool calls ({tool_count}) - could be more efficient"
        }


# ============================================================================
# Problem Resolution Evaluators
# ============================================================================

def resolution_clarity_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluate if the response clearly resolves the customer's issue.

    Checks for:
    - Clear answer to the question
    - Resolution statement
    - Follow-up offer
    """
    response = run.outputs.get("answer", "").lower()
    question = example.inputs.get("question", "").lower()

    resolution_indicators = {
        "direct_answer": [
            "yes", "no", "you can", "the status is", "your order",
            "in stock", "out of stock", "delivered", "in transit"
        ],
        "resolution": [
            "authorized", "processed", "completed", "confirmed",
            "here's what", "here is", "i've", "i have"
        ],
        "follow_up": [
            "anything else", "let me know", "is there", "can i help",
            "need anything", "further assistance"
        ]
    }

    score_components = []
    found = []

    for category, phrases in resolution_indicators.items():
        if any(phrase in response for phrase in phrases):
            score_components.append(1)
            found.append(category)
        else:
            score_components.append(0)

    score = sum(score_components) / len(score_components)

    if score == 1.0:
        return {
            "key": "resolution_clarity",
            "score": 1.0,
            "comment": "Clear resolution with all elements"
        }
    elif score >= 0.66:
        return {
            "key": "resolution_clarity",
            "score": 0.8,
            "comment": f"Good resolution: includes {', '.join(found)}"
        }
    else:
        missing = [cat for cat in resolution_indicators.keys() if cat not in found]
        return {
            "key": "resolution_clarity",
            "score": 0.5,
            "comment": f"Unclear resolution - missing: {', '.join(missing)}"
        }


# ============================================================================
# Combined Evaluator
# ============================================================================

def comprehensive_evaluator(run: Run, example: Example) -> dict:
    """
    A comprehensive evaluator that combines multiple quality checks.

    This is useful for getting an overall quality score.
    """
    # Run sub-evaluators
    evaluators_to_run = [
        empathy_evaluator,
        politeness_evaluator,
        actionability_evaluator,
        specificity_evaluator,
        conciseness_evaluator,
        resolution_clarity_evaluator,
    ]

    scores = []
    comments = []

    for evaluator in evaluators_to_run:
        result = evaluator(run, example)
        scores.append(result["score"])
        if result["score"] < 0.7:  # Only comment on weak areas
            comments.append(f"{result['key']}: {result['comment']}")

    avg_score = sum(scores) / len(scores)

    if avg_score >= 0.9:
        comment = "Excellent overall quality across all dimensions"
    elif avg_score >= 0.7:
        comment = f"Good quality. Areas to improve: {'; '.join(comments) if comments else 'none'}"
    else:
        comment = f"Needs improvement: {'; '.join(comments)}"

    return {
        "key": "comprehensive_quality",
        "score": avg_score,
        "comment": comment
    }


# ============================================================================
# Evaluator Groups
# ============================================================================

# Pre-defined evaluator groups you can use
EMPATHY_EVALUATORS = [empathy_evaluator, politeness_evaluator]
EFFICIENCY_EVALUATORS = [conciseness_evaluator, tool_efficiency_evaluator]
COMPLETENESS_EVALUATORS = [actionability_evaluator, specificity_evaluator, resolution_clarity_evaluator]
ALL_CUSTOM_EVALUATORS = [
    empathy_evaluator,
    politeness_evaluator,
    actionability_evaluator,
    specificity_evaluator,
    conciseness_evaluator,
    tool_efficiency_evaluator,
    resolution_clarity_evaluator,
]
