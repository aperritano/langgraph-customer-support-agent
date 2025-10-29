"""Tests for state management and message handling."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from src.support_agent.state import SupportState
from langgraph.graph.message import add_messages


class TestSupportState:
    """Test the SupportState TypedDict schema."""

    def test_state_accepts_messages(self):
        """Test that state can be created with messages."""
        state: SupportState = {
            "messages": [HumanMessage(content="Hello")]
        }

        assert "messages" in state
        assert len(state["messages"]) == 1
        assert isinstance(state["messages"][0], HumanMessage)

    def test_state_with_empty_messages(self):
        """Test that state can be created with empty message list."""
        state: SupportState = {
            "messages": []
        }

        assert "messages" in state
        assert len(state["messages"]) == 0

    def test_state_with_multiple_message_types(self):
        """Test that state handles different message types."""
        state: SupportState = {
            "messages": [
                SystemMessage(content="You are a helpful assistant"),
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!"),
            ]
        }

        assert len(state["messages"]) == 3
        assert isinstance(state["messages"][0], SystemMessage)
        assert isinstance(state["messages"][1], HumanMessage)
        assert isinstance(state["messages"][2], AIMessage)


class TestAddMessages:
    """Test the add_messages annotation behavior."""

    def test_add_messages_appends_new_messages(self):
        """Test that add_messages appends to existing messages."""
        existing_messages = [HumanMessage(content="First message")]
        new_messages = [AIMessage(content="Second message")]

        result = add_messages(existing_messages, new_messages)

        assert len(result) == 2
        assert result[0].content == "First message"
        assert result[1].content == "Second message"

    def test_add_messages_with_empty_existing(self):
        """Test add_messages when starting with empty list."""
        existing_messages = []
        new_messages = [HumanMessage(content="First message")]

        result = add_messages(existing_messages, new_messages)

        assert len(result) == 1
        assert result[0].content == "First message"

    def test_add_messages_with_multiple_new_messages(self):
        """Test add_messages with multiple new messages."""
        existing_messages = [HumanMessage(content="First")]
        new_messages = [
            AIMessage(content="Second"),
            HumanMessage(content="Third"),
        ]

        result = add_messages(existing_messages, new_messages)

        assert len(result) == 3
        assert result[0].content == "First"
        assert result[1].content == "Second"
        assert result[2].content == "Third"

    def test_add_messages_preserves_message_types(self):
        """Test that message types are preserved when adding."""
        existing_messages = [HumanMessage(content="Human message")]
        new_messages = [
            AIMessage(content="AI response", tool_calls=[]),
            ToolMessage(content="Tool result", tool_call_id="call_1"),
        ]

        result = add_messages(existing_messages, new_messages)

        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert isinstance(result[2], ToolMessage)

    def test_add_messages_preserves_message_attributes(self):
        """Test that message attributes like tool_calls are preserved."""
        existing_messages = []
        new_messages = [
            AIMessage(
                content="Using tool",
                tool_calls=[{
                    "name": "get_order_status",
                    "args": {"order_id": "123"},
                    "id": "call_1"
                }]
            )
        ]

        result = add_messages(existing_messages, new_messages)

        assert len(result) == 1
        assert isinstance(result[0], AIMessage)
        assert len(result[0].tool_calls) == 1
        assert result[0].tool_calls[0]["name"] == "get_order_status"


class TestStateUpdates:
    """Test how state updates work in practice."""

    def test_state_update_with_agent_response(self):
        """Test typical state update from agent node."""
        initial_state: SupportState = {
            "messages": [HumanMessage(content="What's my order status?")]
        }

        # Simulate agent node returning update
        update = {
            "messages": [AIMessage(content="I'll check that for you", tool_calls=[])]
        }

        # Merge using add_messages logic
        new_messages = add_messages(initial_state["messages"], update["messages"])

        assert len(new_messages) == 2
        assert isinstance(new_messages[0], HumanMessage)
        assert isinstance(new_messages[1], AIMessage)

    def test_state_update_with_tool_result(self):
        """Test state update after tool execution."""
        initial_state: SupportState = {
            "messages": [
                HumanMessage(content="Check order 123456"),
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "get_order_status",
                        "args": {"order_id": "123456"},
                        "id": "call_1"
                    }]
                ),
            ]
        }

        # Simulate tool node returning result
        update = {
            "messages": [
                ToolMessage(
                    content="Order 123456 is in transit",
                    tool_call_id="call_1"
                )
            ]
        }

        new_messages = add_messages(initial_state["messages"], update["messages"])

        assert len(new_messages) == 3
        assert isinstance(new_messages[2], ToolMessage)

    def test_conversation_flow_through_states(self):
        """Test a complete conversation flow through multiple state updates."""
        # Start with human message
        state: SupportState = {"messages": []}

        # User asks question
        state["messages"] = add_messages(
            state["messages"],
            [HumanMessage(content="What's the return policy?")]
        )
        assert len(state["messages"]) == 1

        # Agent decides to search knowledge base
        state["messages"] = add_messages(
            state["messages"],
            [AIMessage(
                content="",
                tool_calls=[{
                    "name": "search_vector_knowledge_base",
                    "args": {"query": "return policy"},
                    "id": "call_1"
                }]
            )]
        )
        assert len(state["messages"]) == 2

        # Tool returns result
        state["messages"] = add_messages(
            state["messages"],
            [ToolMessage(
                content="Returns accepted within 30 days",
                tool_call_id="call_1"
            )]
        )
        assert len(state["messages"]) == 3

        # Agent provides final answer
        state["messages"] = add_messages(
            state["messages"],
            [AIMessage(content="You can return items within 30 days")]
        )
        assert len(state["messages"]) == 4

        # Verify message types in order
        assert isinstance(state["messages"][0], HumanMessage)
        assert isinstance(state["messages"][1], AIMessage)
        assert isinstance(state["messages"][2], ToolMessage)
        assert isinstance(state["messages"][3], AIMessage)


class TestMessageContent:
    """Test message content handling."""

    def test_message_content_is_preserved(self):
        """Test that message content strings are preserved exactly."""
        content = "What's the status of order #123456?"
        state: SupportState = {
            "messages": [HumanMessage(content=content)]
        }

        assert state["messages"][0].content == content

    def test_empty_content_is_valid(self):
        """Test that messages can have empty content (e.g., tool-calling messages)."""
        state: SupportState = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "some_tool", "args": {}, "id": "call_1"}]
                )
            ]
        }

        assert state["messages"][0].content == ""
        assert len(state["messages"][0].tool_calls) > 0

    def test_multiline_content(self):
        """Test that multiline content is preserved."""
        content = """Hello,
        I have multiple questions:
        1. What's my order status?
        2. When will it arrive?"""

        state: SupportState = {
            "messages": [HumanMessage(content=content)]
        }

        assert state["messages"][0].content == content
        assert "\n" in state["messages"][0].content
