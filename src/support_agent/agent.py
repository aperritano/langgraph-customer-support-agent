"""Customer support agent graph definition.

This is the main entry point that LangGraph Dev uses to run the agent.
The graph variable at the bottom must be exported for langgraph.json to find it.
"""

from typing import Literal, cast
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from pathlib import Path

from .state import SupportState
from .tools import tools
from .prompts import SYSTEM_PROMPT


# Initialize LLM with tool calling capability
llm = ChatOllama(
    model="llama3.1:latest",  # Change to mistral:7b or qwen2.5:7b if preferred
    temperature=0,  # Deterministic responses for customer support
).bind_tools(tools)


def agent_node(state: SupportState) -> dict:
    """
    Agent reasoning node - decides which tools to call or provides final answer.
    
    This implements the "Reasoning" part of the ReAct pattern.
    The LLM analyzes the conversation and decides whether to:
    1. Call one or more tools to gather information
    2. Provide a final answer to the customer
    
    Args:
        state: Current conversation state with message history
    
    Returns:
        dict with new messages to add to state
    """
    # Prepend system prompt to conversation
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    
    # Invoke LLM - it will decide to call tools or respond directly
    response = llm.invoke(messages)
    
    # Return response as state update
    return {"messages": [response]}


def should_continue(state: SupportState) -> Literal["tools", "__end__"]:
    """
    Conditional edge - decides whether to continue to tools or end.

    This is the decision point in the ReAct loop:
    - If LLM made tool calls → go to tools node to execute them
    - If LLM provided a final answer → end the conversation turn

    Args:
        state: Current conversation state

    Returns:
        "tools" if tool calls exist, "__end__" otherwise
    """
    last_message = state["messages"][-1]

    # Check if the agent made any tool calls
    # Type check: last_message from LLM is always AIMessage which has tool_calls
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    # No tool calls means agent provided final answer
    return "__end__"


def create_graph():
    """
    Build and compile the customer support agent graph.
    
    Graph structure (ReAct pattern):
    
        START
          ↓
       [AGENT] ← Reasoning step: decide to call tools or answer
          ↓
       {should_continue?}
        ↙        ↘
    [TOOLS]    [END]
       ↓
    [AGENT] ← Loop back with tool results
    
    The graph loops between agent and tools until the agent
    provides a final answer without tool calls.
    
    Returns:
        Compiled LangGraph application
    """
    # Initialize graph with our state schema
    workflow = StateGraph(SupportState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))  # Automatically handles all tool execution
    
    # Define the flow
    workflow.add_edge(START, "agent")  # Start at agent
    
    # After agent, decide whether to use tools or end
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # Call tools if needed
            "__end__": END,  # End if agent provided answer
        },
    )
    
    # After tools execute, always go back to agent for next reasoning step
    workflow.add_edge("tools", "agent")

    # Note: When using langgraph dev/cloud, checkpointing is handled automatically
    # For local testing, you can pass a checkpointer to compile()
    return workflow.compile()


# Create and export the graph
# This variable name must match what's in langgraph.json
graph = create_graph()


# For local testing
if __name__ == "__main__":
    """
    Quick test of the graph.
    Run: python -m src.support_agent.agent
    """
    from langchain_core.messages import HumanMessage
    
    print("Testing customer support agent...\n")
    
    # Test conversation
    test_messages = [
        "Hi, what's your return policy?",
        "Can you check on order #123456?",
        "I want to return it because it's defective",
    ]
    
    config = {"configurable": {"thread_id": "test-conversation"}}
    
    for message in test_messages:
        print(f"💬 Customer: {message}")
        print("-" * 60)

        result = graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=cast(RunnableConfig, config)
        )

        # Print the agent's response
        last_message = result["messages"][-1]
        print(f"🤖 Agent: {last_message.content}\n")
