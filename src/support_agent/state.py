"""State schema for customer support agent."""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class SupportState(TypedDict):
    """
    State for customer support conversation.
    
    The only required field is 'messages' which stores the conversation history.
    The add_messages annotation ensures messages are properly accumulated.
    """
    
    messages: Annotated[list[BaseMessage], add_messages]
    """
    Conversation history. The add_messages annotation automatically:
    - Appends new messages to the list
    - Handles message deduplication
    - Maintains proper message ordering
    """
