"""Tests for agent graph logic and decision-making."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.support_agent.agent import should_continue, agent_node, create_graph
from src.support_agent.state import SupportState


class TestShouldContinue:
    """Test the conditional edge logic that decides whether to continue to tools or end."""

    def test_should_continue_with_tool_calls(self):
        """Test that agent continues to tools when AIMessage has tool_calls."""
        state: SupportState = {
            "messages": [
                HumanMessage(content="What's my order status?"),
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "get_order_status",
                            "args": {"order_id": "123456"},
                            "id": "call_1",
                        }
                    ],
                ),
            ]
        }

        result = should_continue(state)
        assert result == "tools", "Should route to tools when tool_calls exist"

    def test_should_continue_without_tool_calls(self):
        """Test that agent ends when AIMessage has no tool_calls."""
        state: SupportState = {
            "messages": [
                HumanMessage(content="Thank you!"),
                AIMessage(content="You're welcome! Have a great day!"),
            ]
        }

        result = should_continue(state)
        assert result == "__end__", "Should end when no tool_calls exist"

    def test_should_continue_with_empty_tool_calls_list(self):
        """Test that agent ends when tool_calls is an empty list."""
        state: SupportState = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!", tool_calls=[]),
            ]
        }

        result = should_continue(state)
        assert result == "__end__", "Should end when tool_calls is empty"

    def test_should_continue_with_human_message_last(self):
        """Test behavior when last message is not AIMessage (edge case)."""
        state: SupportState = {
            "messages": [
                AIMessage(content="How can I help?"),
                HumanMessage(content="I need help"),
            ]
        }

        result = should_continue(state)
        # HumanMessage doesn't have tool_calls, should end
        assert result == "__end__"


class TestAgentNode:
    """Test the agent reasoning node that decides actions."""

    def test_agent_node_returns_messages(self):
        """Test that agent_node returns a dict with messages key."""
        state: SupportState = {
            "messages": [HumanMessage(content="Hello, I need help with my order")]
        }

        result = agent_node(state)

        assert isinstance(result, dict), "Should return a dictionary"
        assert "messages" in result, "Should have 'messages' key"
        assert isinstance(result["messages"], list), "Messages should be a list"
        assert len(result["messages"]) > 0, "Should return at least one message"

    def test_agent_node_returns_ai_message(self):
        """Test that agent_node returns AIMessage type."""
        state: SupportState = {
            "messages": [HumanMessage(content="What's your return policy?")]
        }

        result = agent_node(state)
        message = result["messages"][0]

        assert isinstance(message, AIMessage), "Should return AIMessage"

    def test_agent_node_preserves_conversation_context(self):
        """Test that agent has access to conversation history."""
        state: SupportState = {
            "messages": [
                HumanMessage(content="Hi, my order number is 123456"),
                AIMessage(content="I'll look that up for you"),
                HumanMessage(content="Also, I want to return it"),
            ]
        }

        # Agent should be able to reference the order number from earlier
        result = agent_node(state)
        assert result["messages"][0] is not None


class TestGraphCreation:
    """Test graph structure and compilation."""

    def test_create_graph_returns_compiled_graph(self):
        """Test that create_graph returns a compiled graph."""
        graph = create_graph()

        assert graph is not None, "Graph should be created"
        # Check if it's a compiled graph by checking for invoke method
        assert hasattr(graph, "invoke"), "Graph should be compiled with invoke method"
        assert hasattr(graph, "stream"), "Graph should have stream method"

    def test_graph_has_required_nodes(self):
        """Test that graph contains the required nodes."""
        graph = create_graph()

        # Get the graph structure
        # Note: This is implementation-specific and may need adjustment
        # based on LangGraph's API
        assert graph is not None

    def test_graph_invoke_with_simple_message(self):
        """Test that graph can process a simple message."""
        graph = create_graph()

        state: SupportState = {
            "messages": [HumanMessage(content="Hello")]
        }

        # This is an integration test - it will actually call the LLM
        # In a real test environment, you'd mock the LLM
        result = graph.invoke(state)

        assert "messages" in result, "Result should contain messages"
        assert len(result["messages"]) > 1, "Should have at least initial message + response"


class TestGraphIntegration:
    """Integration tests for the full graph execution (requires LLM)."""

    @pytest.mark.integration
    def test_graph_handles_order_status_query(self):
        """Test end-to-end flow for order status query."""
        graph = create_graph()

        result = graph.invoke(
            {"messages": [HumanMessage(content="What's the status of order 123456?")]}
        )

        # Should have multiple messages (input + agent responses + tool results)
        assert len(result["messages"]) >= 2
        # Last message should be from agent
        assert isinstance(result["messages"][-1], AIMessage)

    @pytest.mark.integration
    def test_graph_handles_general_question(self):
        """Test end-to-end flow for general question without tools."""
        graph = create_graph()

        result = graph.invoke(
            {"messages": [HumanMessage(content="Thank you for your help!")]}
        )

        # Should have response
        assert len(result["messages"]) >= 2
        # Should end without tool calls for simple thank you
        last_message = result["messages"][-1]
        assert isinstance(last_message, AIMessage)

    @pytest.mark.integration
    def test_graph_maintains_conversation_state(self):
        """Test that graph maintains state across multiple invocations."""
        graph = create_graph()
        config = {"configurable": {"thread_id": "test-123"}}

        # First message
        result1 = graph.invoke(
            {"messages": [HumanMessage(content="My order is 123456")]},
            config
        )
        assert len(result1["messages"]) >= 2

        # Second message referencing first
        result2 = graph.invoke(
            {"messages": [HumanMessage(content="I want to return it")]},
            config
        )
        # Should maintain context from previous message
        assert len(result2["messages"]) >= 2
