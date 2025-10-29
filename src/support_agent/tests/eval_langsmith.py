"""
LangSmith Evaluation Script for Customer Support Agent

WHAT THIS FILE DOES:
Creates a comprehensive evaluation suite using LangSmith (LangChain's evaluation
platform). Tests the agent on multiple scenarios, measures performance with various
evaluators, and provides detailed metrics and traces.

WHY IT'S IMPORTANT:
Evaluation ensures the agent works correctly and helps identify areas for improvement.
LangSmith provides:
- Automated testing across many scenarios
- Metrics (tool usage, response quality, etc.)
- Comparison with previous versions
- Detailed traces showing exactly what the agent did
- Visual dashboards for monitoring agent performance

This is like having a comprehensive test suite that also gives you performance metrics.

Run: python -m src.support_agent.tests.eval_langsmith

Requirements:
- LANGCHAIN_API_KEY environment variable set
- LANGCHAIN_TRACING_V2=true (optional, for detailed traces)
"""

import os
from typing import Dict, Any, List
from datetime import datetime

from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langsmith.schemas import Run, Example

from langchain_core.messages import HumanMessage
from src.support_agent.agent import graph

# Import custom evaluators (optional)
try:
    from src.support_agent.tests.custom_evaluators import (
        empathy_evaluator,
        actionability_evaluator,
        EMPATHY_EVALUATORS,
        EFFICIENCY_EVALUATORS,
    )
    CUSTOM_EVALUATORS_AVAILABLE = True
except ImportError:
    CUSTOM_EVALUATORS_AVAILABLE = False


# ============================================================================
# Configuration
# ============================================================================

DATASET_NAME = "customer-support-qa"
EXPERIMENT_PREFIX = "support-agent-eval"

# Ensure LangSmith is configured
if not os.getenv("LANGCHAIN_API_KEY"):
    raise ValueError(
        "LANGCHAIN_API_KEY environment variable not set.\n"
        "Get your API key from: https://smith.langchain.com/settings"
    )

# Initialize LangSmith client
client = Client()


# ============================================================================
# Dataset Creation
# ============================================================================

def create_evaluation_dataset():
    """
    Create a dataset with diverse customer support test cases.
    
    WHAT IT DOES:
    Creates a LangSmith dataset containing various customer scenarios (order status,
    returns, product availability, etc.). Each example defines a customer question
    and expected behavior (which tools should be used, what keywords should appear).

    WHY IT'S IMPORTANT:
    The dataset is what gets evaluated. Without diverse test cases, you can't be
    confident the agent handles different scenarios correctly. This creates a
    comprehensive set of scenarios covering the main use cases.

    Each example includes:
    - inputs: Customer question
    - outputs: Expected response characteristics (not exact text - just what should happen)
    """

    print(f"\n{'='*70}")
    print(f"Creating dataset: {DATASET_NAME}")
    print(f"{'='*70}\n")

    # Check if dataset already exists
    try:
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
        print(f"Dataset '{DATASET_NAME}' already exists (ID: {dataset.id})")
        print(f"Deleting and recreating...")
        client.delete_dataset(dataset_id=dataset.id)
    except Exception:
        pass

    # Create fresh dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Test cases for customer support agent covering various scenarios",
    )
    print(f"Created dataset: {dataset.id}\n")

    # Define test cases
    test_cases = [
        # Knowledge base queries
        {
            "inputs": {"question": "What's your return policy?"},
            "outputs": {
                "should_mention": ["30 days", "return", "refund"],
                "should_use_tool": "search_vector_knowledge_base",
                "category": "return_policy"
            }
        },
        {
            "inputs": {"question": "Do you offer international shipping?"},
            "outputs": {
                "should_mention": ["shipping", "international"],
                "should_use_tool": "search_vector_knowledge_base",
                "category": "shipping"
            }
        },
        {
            "inputs": {"question": "What payment methods do you accept?"},
            "outputs": {
                "should_mention": ["payment", "credit card"],
                "should_use_tool": "search_vector_knowledge_base",
                "category": "payment"
            }
        },

        # Order status queries
        {
            "inputs": {"question": "Can you check the status of order #123456?"},
            "outputs": {
                "should_mention": ["in transit", "tracking"],
                "should_use_tool": "get_order_status",
                "category": "order_status"
            }
        },
        {
            "inputs": {"question": "Where is my order 789012?"},
            "outputs": {
                "should_mention": ["delivered"],
                "should_use_tool": "get_order_status",
                "category": "order_status"
            }
        },

        # Return requests
        {
            "inputs": {"question": "I want to return order #123456 because it's defective"},
            "outputs": {
                "should_mention": ["return", "authorization", "RMA", "free"],
                "should_use_tool": "initiate_return",
                "category": "return_request"
            }
        },

        # Product availability
        {
            "inputs": {"question": "Is the wireless mouse in stock?"},
            "outputs": {
                "should_mention": ["stock", "mouse"],
                "should_use_tool": "check_product_availability",
                "category": "inventory"
            }
        },
        {
            "inputs": {"question": "Do you have any laptops available?"},
            "outputs": {
                "should_mention": ["in stock", "laptop"],
                "should_use_tool": "check_product_availability",
                "category": "inventory"
            }
        },

        # Complex multi-step scenarios
        {
            "inputs": {"question": "Hi! I ordered a keyboard last week but haven't received it yet. Can you help?"},
            "outputs": {
                "should_mention": ["order", "status"],
                "should_use_tool": "get_order_status",
                "category": "complex"
            }
        },

        # Escalation scenarios
        {
            "inputs": {"question": "This is ridiculous! I've been waiting for weeks and nobody can help me!"},
            "outputs": {
                "should_mention": ["apologize", "ticket", "human"],
                "should_use_tool": "escalate_to_human",
                "category": "escalation"
            }
        },
    ]

    # Add examples to dataset
    print("Adding test cases:")
    for i, test_case in enumerate(test_cases, 1):
        category = test_case["outputs"].get("category", "general")
        question = test_case["inputs"]["question"]

        client.create_example(
            dataset_id=dataset.id,
            inputs=test_case["inputs"],
            outputs=test_case["outputs"]
        )
        print(f"  [{i:2d}] {category:20s} | {question[:50]}")

    print(f"\nDataset created with {len(test_cases)} examples")
    print(f"View at: https://smith.langchain.com/datasets/{dataset.id}\n")

    return dataset


# ============================================================================
# Agent Runner
# ============================================================================

def run_support_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the customer support agent and return structured output.
    
    WHAT IT DOES:
    Wraps the agent graph invocation for evaluation. Takes a customer question,
    runs it through the agent, and returns structured data (response, tools used, etc.)
    that evaluators can check.

    WHY IT'S IMPORTANT:
    This is the function that LangSmith calls for each test case. It needs to
    return structured data so evaluators can check if the agent:
    - Used the correct tools
    - Mentioned expected keywords
    - Provided quality responses

    Args:
        inputs: Dictionary with 'question' key (the customer's question)

    Returns:
        Dictionary with:
        - answer: Agent's final response text
        - tools_used: List of tools the agent called
        - message_count: Total messages in conversation (indicates conversation length)
    """
    question = inputs["question"]

    # Create config with unique thread ID for each run
    config = {
        "configurable": {
            "thread_id": f"eval-{hash(question)}"
        }
    }

    # Invoke the agent
    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config
    )

    # Extract the final response
    final_message = result["messages"][-1]
    response_text = final_message.content if hasattr(final_message, 'content') else str(final_message)

    # Extract tool calls from message history
    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tools_used.append(tool_call.get('name', 'unknown'))

    return {
        "answer": response_text,
        "tools_used": tools_used,
        "message_count": len(result["messages"])
    }


# ============================================================================
# Custom Evaluators
# ============================================================================

def tool_usage_evaluator(run: Run, example: Example) -> dict:
    """
    Check if the agent used the expected tool.
    
    WHAT IT DOES:
    Verifies that the agent called the correct tool(s) for the customer's question.
    For example, checks that a question about order status resulted in calling
    get_order_status, not search_knowledge_base.

    WHY IT'S IMPORTANT:
    Ensures the agent has good "decision-making" - it should use the right tools
    for the right situations. If the agent uses wrong tools, it wastes time and
    gives worse answers.

    This evaluator verifies the agent is calling the right tools
    for different types of customer queries.
    """
    # Get actual tools used
    tools_used = run.outputs.get("tools_used", [])

    # Get expected tool
    expected_tool = example.outputs.get("should_use_tool")

    if not expected_tool:
        return {
            "key": "tool_usage",
            "score": 1.0,
            "comment": "No specific tool required"
        }

    # Check if expected tool was used
    if expected_tool in tools_used:
        return {
            "key": "tool_usage",
            "score": 1.0,
            "comment": f"Correctly used {expected_tool}"
        }
    else:
        return {
            "key": "tool_usage",
            "score": 0.0,
            "comment": f"Expected {expected_tool}, but used: {', '.join(tools_used) if tools_used else 'no tools'}"
        }


def keyword_presence_evaluator(run: Run, example: Example) -> dict:
    """
    Check if the response mentions expected keywords.
    
    WHAT IT DOES:
    Checks that the agent's response contains relevant keywords. For example, if
    asked about returns, the response should mention words like "return", "refund",
    "policy", etc.

    WHY IT'S IMPORTANT:
    Verifies that responses are actually relevant to the question. A response that
    doesn't mention any expected keywords is likely off-topic or unhelpful.
    This is a basic check for response quality.

    This evaluator ensures the agent's response contains
    relevant information for the customer's question.
    """
    # Get agent's response
    response = run.outputs.get("answer", "").lower()

    # Get expected keywords
    expected_keywords = example.outputs.get("should_mention", [])

    if not expected_keywords:
        return {
            "key": "keyword_presence",
            "score": 1.0,
            "comment": "No specific keywords required"
        }

    # Check how many keywords are present
    keywords_found = [kw for kw in expected_keywords if kw.lower() in response]
    score = len(keywords_found) / len(expected_keywords)

    if score == 1.0:
        return {
            "key": "keyword_presence",
            "score": score,
            "comment": f"All keywords present: {', '.join(keywords_found)}"
        }
    elif score > 0:
        missing = set(expected_keywords) - set(keywords_found)
        return {
            "key": "keyword_presence",
            "score": score,
            "comment": f"Partial match. Missing: {', '.join(missing)}"
        }
    else:
        return {
            "key": "keyword_presence",
            "score": 0.0,
            "comment": f"None of expected keywords found: {', '.join(expected_keywords)}"
        }


def response_quality_evaluator(run: Run, example: Example) -> dict:
    """
    Check basic response quality metrics.

    Ensures the response is not too short, not too long,
    and appears to be a complete answer.
    """
    response = run.outputs.get("answer", "")

    # Check response length
    word_count = len(response.split())

    if word_count < 10:
        return {
            "key": "response_quality",
            "score": 0.3,
            "comment": f"Response too short ({word_count} words)"
        }
    elif word_count > 500:
        return {
            "key": "response_quality",
            "score": 0.7,
            "comment": f"Response very long ({word_count} words) - might be too verbose"
        }

    # Check if response looks complete (ends with punctuation)
    if not response.strip() or response.strip()[-1] not in '.!?':
        return {
            "key": "response_quality",
            "score": 0.5,
            "comment": "Response appears incomplete (no ending punctuation)"
        }

    return {
        "key": "response_quality",
        "score": 1.0,
        "comment": f"Good response quality ({word_count} words)"
    }


# ============================================================================
# LLM-as-Judge Evaluators
# ============================================================================

def create_llm_evaluators() -> List[LangChainStringEvaluator]:
    """
    Create LLM-based evaluators that use GPT-4 to judge responses.

    These are more sophisticated than rule-based evaluators and can
    judge subjective qualities like helpfulness and professionalism.
    """

    # Helpfulness evaluator
    helpfulness_evaluator = LangChainStringEvaluator(
        "labeled_criteria",
        config={
            "criteria": {
                "helpfulness": (
                    "Does the response directly address the customer's question? "
                    "Does it provide actionable information or next steps? "
                    "Is it clear and easy to understand?"
                )
            }
        },
        prepare_data=lambda run, example: {
            "prediction": run.outputs["answer"],
            "input": example.inputs["question"]
        }
    )

    # Professionalism evaluator
    professionalism_evaluator = LangChainStringEvaluator(
        "labeled_criteria",
        config={
            "criteria": {
                "professionalism": (
                    "Is the tone professional and courteous? "
                    "Does it avoid being too casual or too robotic? "
                    "Is it empathetic when appropriate?"
                )
            }
        },
        prepare_data=lambda run, example: {
            "prediction": run.outputs["answer"],
            "input": example.inputs["question"]
        }
    )

    return [helpfulness_evaluator, professionalism_evaluator]


# ============================================================================
# Main Evaluation
# ============================================================================

def run_evaluation():
    """
    Run the complete evaluation suite and display results.
    
    WHAT IT DOES:
    Orchestrates the entire evaluation process:
    1. Creates/verifies the test dataset
    2. Prepares all evaluators (tool usage, keywords, quality, etc.)
    3. Runs each test case through the agent
    4. Collects scores from all evaluators
    5. Displays summary and links to detailed results

    WHY IT'S IMPORTANT:
    This is the main entry point that runs everything. Without this orchestration,
    you'd have to manually run tests and check results. This automates the entire
    evaluation workflow and provides a summary of how well the agent performs.
    """
    print(f"\n{'='*70}")
    print(f"CUSTOMER SUPPORT AGENT EVALUATION")
    print(f"{'='*70}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Experiment: {EXPERIMENT_PREFIX}")
    print(f"{'='*70}\n")

    # Step 1: Create/verify dataset
    dataset = create_evaluation_dataset()

    # Step 2: Prepare evaluators
    print(f"{'='*70}")
    print("Preparing Evaluators")
    print(f"{'='*70}\n")

    evaluators = [
        tool_usage_evaluator,
        keyword_presence_evaluator,
        response_quality_evaluator,
    ]

    evaluator_names = [
        "Tool Usage Checker",
        "Keyword Presence Checker",
        "Response Quality Checker",
    ]

    # Add custom evaluators if available
    if CUSTOM_EVALUATORS_AVAILABLE:
        evaluators.extend([empathy_evaluator, actionability_evaluator])
        evaluator_names.extend(["Empathy Checker", "Actionability Checker"])

    # Add LLM evaluators (commented out by default to save costs)
    # Uncomment to enable GPT-4 based evaluation
    # evaluators.extend(create_llm_evaluators())
    # evaluator_names.extend(["Helpfulness (LLM)", "Professionalism (LLM)"])

    for name in evaluator_names:
        print(f"  - {name}")

    print(f"\n{'='*70}")
    print("Running Evaluation")
    print(f"{'='*70}\n")

    # Step 3: Run evaluation
    results = evaluate(
        run_support_agent,
        data=DATASET_NAME,
        evaluators=evaluators,
        experiment_prefix=EXPERIMENT_PREFIX,
        metadata={
            "version": "1.0",
            "model": "llama3.1:latest",
            "description": "Comprehensive evaluation of customer support agent",
            "date": datetime.now().isoformat(),
        },
        max_concurrency=2,  # Run 2 examples in parallel
    )

    # Step 4: Display results
    print(f"\n{'='*70}")
    print("EVALUATION COMPLETE!")
    print(f"{'='*70}\n")

    print(f"Results Summary:")
    print(f"  - Total Examples: 10")
    print(f"  - Evaluators Run: {len(evaluator_names)}")

    # Try to extract and display scores from results
    print(f"\n{'='*70}")
    print("EVALUATION SCORES")
    print(f"{'='*70}\n")

    # The results object is an iterator of ExperimentResultRow objects
    # We need to consume it to see the feedback
    try:
        # Access the summary_metrics if available
        summary_results = client.read_project(project_name=results.experiment_name if hasattr(results, 'experiment_name') else EXPERIMENT_PREFIX)
        if hasattr(summary_results, 'feedback_stats'):
            print("Feedback statistics:")
            for key, stats in summary_results.feedback_stats.items():
                if hasattr(stats, 'avg') and stats.avg is not None:
                    print(f"  - {key:25s}: {stats.avg:.2%}")
    except Exception:
        # If we can't get summary stats, inform user to check online
        print("Scores are being calculated in LangSmith...")
        print("View detailed metrics in the web interface (link below)")

    print(f"\n✅ Evaluation finished successfully!")
    print(f"\nTo see detailed scores and traces for each test:")
    print(f"  1. Click the link shown above during evaluation")
    print(f"  2. Or visit: https://smith.langchain.com/projects")
    print(f"  3. Search for: {EXPERIMENT_PREFIX}")

    print(f"\n{'='*70}")
    print("VIEW RESULTS ONLINE")
    print(f"{'='*70}\n")
    print(f"Dataset:")
    print(f"  https://smith.langchain.com/datasets/{dataset.id}\n")
    print(f"Experiment Results:")
    print(f"  https://smith.langchain.com/projects\n")
    print(f"Search for: {EXPERIMENT_PREFIX}")

    print(f"\n{'='*70}")
    print("WHAT TO CHECK IN LANGSMITH")
    print(f"{'='*70}\n")
    print("In the LangSmith dashboard you'll see:")
    print("  ✓ Aggregate scores for each evaluator")
    print("  ✓ Pass/fail status for each test case")
    print("  ✓ Detailed feedback comments")
    print("  ✓ Full conversation traces")
    print("  ✓ Tool calls made by the agent")
    print("  ✓ Comparison with previous runs")
    print(f"\n{'='*70}\n")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        run_evaluation()
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
