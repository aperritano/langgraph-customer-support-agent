"""Customer Support Agent - A LangGraph-powered support bot.

WHAT THIS FILE DOES:
This is the main package entry point. It exports the key components that other code
(or users of this package) will need: the graph, state schema, and tools list.

WHY IT'S IMPORTANT:
When someone imports from this package (e.g., `from src.support_agent import graph`),
they get these essential components. This is Python's way of defining what's the
"public API" of your package - what other code can and should use.
"""

# Export the compiled graph - this is what runs the agent
# WHAT: The executable LangGraph that processes customer messages
# WHY: This is the main thing users will want - the agent itself
from .agent import graph

# Export the state schema - defines the data structure
# WHAT: The TypedDict that defines conversation state structure
# WHY: Useful for type hints and understanding what data flows through the graph
from .state import SupportState

# Export the tools list - all actions the agent can take
# WHAT: List of all available tools (functions the agent can call)
# WHY: Useful for inspection, debugging, or dynamically adding/removing tools
from .tools import tools

__version__ = "0.1.0"

# What gets imported when someone does "from src.support_agent import *"
# This controls the public API of the package
__all__ = ["graph", "SupportState", "tools"]
