"""State schema for customer support agent.

WHAT THIS FILE DOES:
Defines the data structure that represents the current state of a conversation.
Think of it like a container that holds all the messages in a conversation.

WHY IT'S IMPORTANT:
LangGraph needs to know what data structure to use when passing state between nodes.
This TypedDict tells LangGraph exactly what fields exist and how to handle them.
Without this, the graph wouldn't know how to store and manage conversation history.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class SupportState(TypedDict):
    """
    State for customer support conversation.
    
    WHAT IT IS:
    A TypedDict that defines the shape of data that flows through the graph.
    Currently contains just 'messages' which stores all conversation messages
    (customer questions, agent responses, tool results, etc.)
    
    WHY IT'S IMPORTANT:
    - LangGraph uses this to know what data structure to expect
    - The add_messages annotation handles automatic message merging
    - TypedDict gives us type safety (TypeScript-like typing for Python)
    - All nodes in the graph use this same state structure
    
    The add_messages annotation automatically:
    - Appends new messages to the list (doesn't replace the whole list)
    - Handles message deduplication (prevents duplicates)
    - Maintains proper message ordering (important for conversation context)
    """
    
    messages: Annotated[list[BaseMessage], add_messages]
    """
    Conversation history - the complete record of the conversation.
    
    WHAT IT CONTAINS:
    A list of message objects that can be:
    - HumanMessage: Customer's questions/messages
    - AIMessage: Agent's responses (may include tool_calls)
    - ToolMessage: Results from tool execution
    - SystemMessage: Instructions for the agent
    
    WHY add_messages IS IMPORTANT:
    Without this annotation, when a node returns {"messages": [new_message]},
    LangGraph would replace the entire message list. With add_messages, it
    automatically appends the new message to the existing list. This is crucial
    because we need to maintain conversation history for context.
    
    Example flow:
    1. Customer: "What's my order status?"
       -> messages = [HumanMessage("What's my order status?")]
    
    2. Agent decides to use tool
       -> messages = [HumanMessage(...), AIMessage(tool_calls=[...])]
    
    3. Tool executes and returns result
       -> messages = [HumanMessage(...), AIMessage(...), ToolMessage(...)]
    
    4. Agent uses tool result to respond
       -> messages = [HumanMessage(...), AIMessage(...), ToolMessage(...), AIMessage("Your order is...")]
    """
