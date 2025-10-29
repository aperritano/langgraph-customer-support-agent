"""Customer support agent graph definition.

This is the main entry point that LangGraph Dev uses to run the agent.
The graph variable at the bottom must be exported for langgraph.json to find it.

WHAT THIS FILE DOES:
This file defines the "brain" of the customer support agent - it's like the main controller
that orchestrates the conversation flow. It sets up:
1. The AI model that makes decisions
2. The workflow that processes customer messages
3. The logic for when to use tools vs when to respond directly

WHY IT'S IMPORTANT:
Without this file, the agent wouldn't know how to process customer questions or decide
when to search the knowledge base, check order status, or escalate to humans.
This is the core orchestration layer that makes the agent work as a cohesive system.
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


# Initialize LLM (Large Language Model) with tool calling capability
# WHAT: This creates the AI model that will make decisions and respond to customers
# WHY: The LLM needs to be "bound" to tools so it knows what actions it can take
#      (like searching the knowledge base or checking order status)
#      Temperature=0 makes responses more predictable/consistent, which is important
#      for customer support where you want reliable, professional answers
llm = ChatOllama(
    model="llama3.1:latest",  # Change to mistral:7b or qwen2.5:7b if preferred
    temperature=0,  # Deterministic responses for customer support
).bind_tools(tools)


def agent_node(state: SupportState) -> dict:
    """
    Agent reasoning node - decides which tools to call or provides final answer.
    
    WHAT IT DOES:
    This is the "thinking" step where the AI analyzes what the customer asked and decides:
    1. Does it need more information? → Call tools (search KB, check order, etc.)
    2. Does it have enough info? → Respond directly to the customer
    
    WHY IT'S IMPORTANT:
    This function implements the "Reason" step in the ReAct pattern (Reason → Act → Observe).
    Without this, the agent wouldn't know when to use tools vs when to answer directly.
    It's like the agent's decision-making brain that evaluates each customer message.
    
    HOW IT WORKS:
    - Takes the conversation history (state)
    - Adds the system prompt (instructions for the agent)
    - Sends it all to the LLM
    - LLM responds with either tool calls OR a direct answer
    - Returns the LLM's response to be added to the conversation
    
    Args:
        state: Current conversation state with message history
    
    Returns:
        dict with new messages to add to state (either tool calls or direct response)
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

    WHAT IT DOES:
    This is a routing function that looks at the last message from the agent and decides:
    - "tools" → Agent wants to use tools, so route to the tools node
    - "__end__" → Agent gave a final answer, so we're done with this turn

    WHY IT'S IMPORTANT:
    The graph needs to know where to go next after the agent thinks. This function
    acts like a traffic controller, directing the conversation flow. Without it,
    the graph wouldn't know whether to execute tools or finish responding to the customer.
    
    This is the key decision point that makes the ReAct loop work - it determines
    whether we need another cycle (Reason → Act) or if we're done.

    Args:
        state: Current conversation state with all messages so far

    Returns:
        "tools" if agent wants to call tools, "__end__" if agent gave final answer
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
    
    WHAT IT DOES:
    This function assembles the complete workflow graph that processes customer messages.
    Think of it like building a flowchart that shows how messages flow through the system.
    
    Graph structure (ReAct pattern):
    
        START (customer sends message)
          ↓
       [AGENT] ← AI thinks: "Do I need tools or can I answer directly?"
          ↓
       {should_continue?} ← Decision point: tool calls or final answer?
        ↙        ↘
    [TOOLS]    [END] ← Done! Send response to customer
       ↓
    [AGENT] ← Loop back with tool results, AI thinks again with new info
    
    WHY IT'S IMPORTANT:
    This function creates the actual executable graph that LangGraph will run.
    Without it, you'd just have functions but no way to connect them into a working system.
    The graph structure implements the ReAct pattern which allows the agent to:
    - Think (Reason)
    - Take actions using tools (Act)
    - See results (Observe)
    - Think again with new information
    - Repeat until it has an answer
    
    HOW IT WORKS:
    1. Creates a StateGraph with our SupportState schema (defines data structure)
    2. Adds two nodes: "agent" (thinking) and "tools" (doing actions)
    3. Sets up flow: START → agent → decision → tools OR end
    4. After tools run, loops back to agent so it can use the tool results
    5. Compiles it all into an executable graph
    
    Returns:
        Compiled LangGraph application ready to process customer messages
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
# WHAT: This creates the actual graph instance that will be used throughout the application
# WHY: LangGraph Dev looks for a variable named "graph" in this file to run the agent.
#      This is the entry point that other parts of the system (CLI, API, tests) will use.
#      It's created once when this module is imported, then reused for all conversations.
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
