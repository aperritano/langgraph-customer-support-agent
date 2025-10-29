"""Pytest configuration and shared fixtures for support agent tests.

WHAT THIS FILE DOES:
Sets up shared test configuration and reusable test data (fixtures) that multiple
test files can use. This prevents code duplication across tests.

WHY IT'S IMPORTANT:
Without this file, each test file would need to create its own sample messages and
test data. This file provides common test utilities that all tests can share, making
tests cleaner and easier to maintain.
"""

import pytest


def pytest_configure(config):
    """
    Configure custom pytest markers.
    
    WHAT IT DOES:
    Registers custom markers that can be used to categorize tests (e.g., @pytest.mark.integration).
    
    WHY IT'S IMPORTANT:
    Allows filtering tests - you can run only unit tests (fast) or only integration tests (slower).
    This is useful during development when you want quick feedback from unit tests,
    and run integration tests separately.
    """
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require LLM, slower)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, no external dependencies)"
    )


@pytest.fixture
def sample_human_message():
    """
    Fixture providing a sample human message.
    
    WHAT IT DOES:
    Creates a reusable HumanMessage object that tests can use.
    
    WHY IT'S IMPORTANT:
    Tests need sample data to work with. This fixture provides a standard example
    that many tests can reuse, making tests more consistent and easier to write.
    """
    from langchain_core.messages import HumanMessage
    return HumanMessage(content="Hello, I need help with my order")


@pytest.fixture
def sample_ai_message():
    """Fixture providing a sample AI message."""
    from langchain_core.messages import AIMessage
    return AIMessage(content="I'd be happy to help you with your order!")


@pytest.fixture
def sample_ai_message_with_tool_call():
    """Fixture providing an AI message with tool calls."""
    from langchain_core.messages import AIMessage
    return AIMessage(
        content="",
        tool_calls=[{
            "name": "get_order_status",
            "args": {"order_id": "123456"},
            "id": "call_123"
        }]
    )


@pytest.fixture
def sample_tool_message():
    """Fixture providing a sample tool message."""
    from langchain_core.messages import ToolMessage
    return ToolMessage(
        content="Order 123456 is in transit",
        tool_call_id="call_123"
    )


@pytest.fixture
def basic_conversation_state():
    """Fixture providing a basic conversation state."""
    from langchain_core.messages import HumanMessage, AIMessage
    from src.support_agent.state import SupportState

    state: SupportState = {
        "messages": [
            HumanMessage(content="What's the return policy?"),
            AIMessage(content="Our return policy allows returns within 30 days"),
        ]
    }
    return state
