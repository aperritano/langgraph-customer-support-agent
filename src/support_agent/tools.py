"""Customer support tools using @tool decorator.

WHAT THIS FILE DOES:
Defines all the "actions" the agent can take to help customers. These are functions
that the AI can call when it needs to do something like check order status, search
the knowledge base, or initiate a return.

WHY IT'S IMPORTANT:
Tools give the agent capabilities beyond just talking. Without tools, the agent
could only provide generic answers. With tools, it can:
- Look up real information (order status, product availability)
- Perform actions (initiate returns, escalate to humans)
- Search knowledge bases for accurate policy information

Think of tools like the buttons on a remote control - they're the actual actions
the agent can take, not just words it can say.

HOW TOOLS WORK:
1. Each function is decorated with @tool (from LangChain)
2. The decorator automatically creates a tool description that the LLM can read
3. When the agent decides to use a tool, LangGraph calls the function
4. The function returns a string result that gets added to the conversation
5. The agent then uses this result to formulate its response to the customer
"""

from langchain_core.tools import tool
from datetime import datetime, timedelta
import json
from pathlib import Path
from .vector_store import get_vector_store


# Mock data - in production, replace with real database/API calls
# WHAT: Sample order and inventory data for testing/demo purposes
# WHY: In a real system, these would be database queries or API calls to your
#      order management system and inventory system. For demo/development, we use
#      hardcoded data so the tools work without setting up external services.
MOCK_ORDERS = {
    "123456": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=2)).strftime("%b %d, %Y"),
        "tracking": "1Z999AA10123456784",
        "items": ["Wireless Headphones", "USB Cable"],
    },
    "789012": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=3)).strftime("%b %d, %Y"),
        "items": ["Laptop Stand"],
    },
    "345678": {
        "status": "processing",
        "expected_ship": (datetime.now() + timedelta(days=1)).strftime("%b %d, %Y"),
        "items": ["Mechanical Keyboard", "Mouse Pad"],
    },
}

MOCK_INVENTORY = {
    "laptop": {"stock": 15, "status": "in_stock"},
    "headphones": {"stock": 3, "status": "low_stock"},
    "mouse": {"stock": 0, "status": "out_of_stock", "restock_date": "Nov 5, 2025"},
    "keyboard": {"stock": 25, "status": "in_stock"},
    "monitor": {"stock": 8, "status": "in_stock"},
    "webcam": {"stock": 1, "status": "low_stock"},
}


@tool
def search_knowledge_base(query: str, category: str = "general") -> str:
    """
    Search the store's knowledge base for information about policies, products, and FAQ.
    
    WHAT IT DOES:
    Searches the vector store (semantic search) to find relevant information based on
    the customer's question. This is like searching a company's internal wiki or FAQ.
    
    WHY IT'S IMPORTANT:
    Instead of hardcoding policies in the prompt (which would make them hard to update),
    this tool allows the agent to search a searchable knowledge base. When policies change,
    you only update the knowledge base, not the code. Also enables more accurate, specific
    answers since it searches the actual content rather than relying on the LLM's training data.
    
    HOW IT WORKS:
    1. Takes the customer's question (query) and optional category filter
    2. Calls the vector store's search function (semantic similarity search)
    3. Returns formatted results from the knowledge base
    4. Agent uses these results to answer the customer's question

    Use this tool to find answers about:
    - Store policies (returns, shipping, warranties)
    - Product information and features
    - Payment methods and security
    - General customer service questions

    Args:
        query: The customer's question or search terms
        category: Type of information needed. Options:
                 - "product": Product features, specifications, warranties
                 - "shipping": Delivery times, shipping costs, tracking
                 - "return": Return policies, refund process, exchanges
                 - "payment": Payment methods, security, billing
                 - "general": Other questions

    Returns:
        Relevant information from the knowledge base
    """
    # Get vector store instance
    vector_store = get_vector_store()

    # Use vector search with category filter
    filter_category = None if category == "general" else category
    results = vector_store.search(query, k=3, filter_category=filter_category)

    return f"Knowledge Base - {category.title()} Information:\n\n{results}"


@tool
def get_order_status(order_id: str) -> str:
    """
    Look up the current status and tracking information for a customer's order.
    
    WHAT IT DOES:
    Queries the order management system (currently mock data) to get the current status
    of a customer's order, including tracking information, delivery dates, and items.

    WHY IT'S IMPORTANT:
    Customers frequently ask "Where is my order?" or "When will my order arrive?"
    This tool gives the agent the ability to answer these questions accurately by
    looking up real order data. Without this, the agent would have to guess or say
    it doesn't know, which would be a bad customer experience.
    
    HOW IT WORKS:
    1. Takes order ID from customer message (agent extracts it)
    2. Looks up order in MOCK_ORDERS (in production, would query database/API)
    3. Formats status information in a customer-friendly way
    4. Returns status, tracking number, delivery date, and items
    
    Use this tool when customers ask about:
    - Where is my order?
    - When will my order arrive?
    - Has my order shipped?
    - Order tracking information
    
    Args:
        order_id: The order number (typically 6+ digits, may include letters)
    
    Returns:
        Current order status, expected delivery date, and tracking information
    """
    # Clean up order ID (remove # if present)
    order_id = order_id.replace("#", "").strip()
    
    # Look up order
    order = MOCK_ORDERS.get(order_id)
    
    if not order:
        return f"""Order #{order_id} not found.

Please verify the order number and try again. Order numbers are typically 6 digits and can be found in your confirmation email.

If you continue to have trouble, I can escalate this to a human agent who can help locate your order."""
    
    # Format response based on status
    if order["status"] == "in_transit":
        return f"""📦 Order #{order_id} - In Transit

Status: Your order is on its way!
Expected Delivery: {order['expected_delivery']}
Tracking Number: {order['tracking']}
Items: {', '.join(order['items'])}

You can track your package at: https://track.example.com/{order['tracking']}"""
    
    elif order["status"] == "delivered":
        return f"""✅ Order #{order_id} - Delivered

Status: Successfully delivered
Delivered: {order['delivered_date']}
Items: {', '.join(order['items'])}

If you haven't received your package or there are any issues, please let me know and I can help!"""
    
    elif order["status"] == "processing":
        return f"""⏳ Order #{order_id} - Processing

Status: Your order is being prepared for shipment
Expected Ship Date: {order['expected_ship']}
Items: {', '.join(order['items'])}

You'll receive a tracking number via email as soon as your order ships. Thanks for your patience!"""
    
    return f"Order #{order_id} status: {order['status']}"


@tool
def initiate_return(order_id: str, reason: str) -> str:
    """
    Start the return process for a customer's order.
    
    WHAT IT DOES:
    Creates a return authorization (RMA) and provides the customer with step-by-step
    instructions for returning their item. Handles different return types (defective
    items get free shipping, regular returns have a shipping fee).

    WHY IT'S IMPORTANT:
    Processing returns manually is time-consuming. This tool automates the initial
    return authorization, generates an RMA number, and gives customers clear instructions.
    The agent can initiate returns in conversation without needing a human agent to do it.
    
    HOW IT WORKS:
    1. Takes order ID and return reason from customer message
    2. Verifies order exists
    3. Generates return authorization number (RMA)
    4. Determines if return is free (defective/damaged) or paid (other reasons)
    5. Returns formatted instructions with RMA number and steps
    
    Use this tool when customers want to:
    - Return an item
    - Get a refund
    - Exchange a product
    - Report a defective item
    
    Args:
        order_id: The order number to return
        reason: Why the customer wants to return. Common reasons:
                - "defective": Item is broken or not working properly
                - "wrong_item": Received incorrect item
                - "changed_mind": Customer no longer wants the item
                - "not_as_described": Item doesn't match description
                - "damaged": Item arrived damaged
    
    Returns:
        Return authorization details and next steps
    """
    # Clean up order ID
    order_id = order_id.replace("#", "").strip()
    
    # Verify order exists
    order = MOCK_ORDERS.get(order_id)
    
    if not order:
        return f"I couldn't find order #{order_id}. Please verify the order number and try again."
    
    # Generate return authorization (in production, this would create a database entry)
    return_id = f"RMA-{order_id}-{hash(reason) % 1000:03d}"
    
    # Different process for defective items
    if "defect" in reason.lower() or "damaged" in reason.lower() or "broken" in reason.lower():
        return f"""🔄 Return Authorized - Order #{order_id}

Return Authorization: {return_id}
Reason: {reason}
Items: {', '.join(order['items'])}

Since your item is defective/damaged, we'll make this easy:

1. ✅ FREE return shipping label will be emailed to you within 1 hour
2. 📦 Pack the item securely in any box
3. 📧 Print the label and attach it to the package
4. 🚚 Drop off at any UPS location or schedule a pickup
5. 💰 Full refund processed within 5-7 business days after we receive it

We apologize for the inconvenience! Is there anything else I can help with?"""
    
    else:
        return f"""🔄 Return Authorized - Order #{order_id}

Return Authorization: {return_id}
Reason: {reason}
Items: {', '.join(order['items'])}

Here's how to return your order:

1. 📧 Return label will be emailed to you within 1 hour ($7.99 deducted from refund)
2. 📦 Pack the item in original packaging with all accessories and tags
3. 🏷️ Print the label and attach it to the package
4. 🚚 Drop off at any UPS location
5. 💰 Refund processed within 5-7 business days after we receive it

Note: Items must be unused and in original condition for a full refund.
Would you like to proceed with this return?"""


@tool
def check_product_availability(product_name: str) -> str:
    """
    Check if a product is currently in stock and available for purchase.
    
    WHAT IT DOES:
    Queries the inventory system to check if a product is available, how many units
    are in stock, and when out-of-stock items might be restocked.

    WHY IT'S IMPORTANT:
    Customers often ask "Do you have X in stock?" before ordering. This tool allows
    the agent to give real-time inventory information, helping customers make
    purchasing decisions and setting expectations about availability.
    
    HOW IT WORKS:
    1. Takes product name from customer query
    2. Searches MOCK_INVENTORY (in production, queries inventory database/API)
    3. Matches product names (case-insensitive, partial matching)
    4. Returns stock status, quantity, and restock date if out of stock
    
    Use this tool when customers ask:
    - Is [product] in stock?
    - Do you have [product] available?
    - When will [product] be back in stock?
    - Can I order [product] now?
    
    Args:
        product_name: Name or description of the product to check
    
    Returns:
        Stock status and availability information
    """
    # Normalize product name
    product_lower = product_name.lower()
    
    # Check inventory
    found_products = []
    for product_key, details in MOCK_INVENTORY.items():
        if product_key in product_lower or product_lower in product_key:
            found_products.append((product_key, details))
    
    if not found_products:
        return f"""I couldn't find specific inventory information for "{product_name}".

Please provide more details or check our online catalog at www.store.com/products

Would you like me to help you find something similar, or would you like to speak with a product specialist?"""
    
    # Format results
    results = []
    for product_key, details in found_products:
        stock_count = details["stock"]
        status = details["status"]
        
        if status == "in_stock":
            results.append(
                f"✅ {product_key.title()}: IN STOCK ({stock_count} units available)\n"
                f"   Ready to ship within 1-2 business days!"
            )
        elif status == "low_stock":
            results.append(
                f"⚠️ {product_key.title()}: LOW STOCK ({stock_count} units remaining)\n"
                f"   Order soon to avoid missing out!"
            )
        elif status == "out_of_stock":
            restock = details.get("restock_date", "TBD")
            results.append(
                f"❌ {product_key.title()}: OUT OF STOCK\n"
                f"   Expected restock: {restock}\n"
                f"   Would you like me to notify you when it's back in stock?"
            )
    
    return "\n\n".join(results)


@tool
def search_vector_knowledge_base(
    query: str,
    max_results: int = 5,
    min_similarity_score: float = 0.0,
    categories: str = ""
) -> str:
    """
    Advanced vector search across the knowledge base with similarity scoring.
    
    WHAT IT DOES:
    Performs semantic similarity search (not just keyword matching) across the
    knowledge base. This can find relevant information even when the wording doesn't
    exactly match. Includes similarity scores so you can filter by relevance.

    WHY IT'S IMPORTANT:
    This is more powerful than the basic search_knowledge_base because:
    - Semantic search understands meaning, not just keywords
    - Similarity scores help judge information quality
    - Can filter by categories for more targeted results
    - Useful for complex questions that need multiple information sources
    
    HOW IT WORKS:
    1. Converts query into embedding (vector representation of meaning)
    2. Compares against all documents in vector store using cosine similarity
    3. Returns top results with similarity scores (0.0 to 1.0)
    4. Filters by minimum score threshold and optional categories

    Use this tool for complex queries that need:
    - Semantic similarity matching (finds conceptually related content)
    - Filtering by relevance scores
    - Multi-category search
    - More comprehensive results than basic search

    This is more powerful than search_knowledge_base for:
    - Complex customer questions requiring multiple information sources
    - Finding related information across different policy areas
    - When you need to see relevance scores to judge information quality
    - Broader searches that might span multiple categories

    Args:
        query: The customer's question or search terms (uses semantic similarity)
        max_results: Maximum number of results to return (1-10, default: 5)
        min_similarity_score: Minimum similarity score threshold 0.0-1.0 (default: 0.0)
                             Higher values = stricter matching. Typical values:
                             - 0.0: Return all results (most permissive)
                             - 0.3: Somewhat related content
                             - 0.5: Moderately related content
                             - 0.7: Highly related content (strictest)
        categories: Comma-separated list of categories to search (optional).
                   Valid categories: product, shipping, return, payment, general
                   Example: "return,payment" searches only those categories
                   Leave empty to search all categories

    Returns:
        Formatted search results with similarity scores and source categories
    """
    # Get vector store instance
    vector_store = get_vector_store()

    # Validate and constrain max_results (handle string input from LLM)
    if isinstance(max_results, str):
        max_results = int(max_results) if max_results.isdigit() else 5
    max_results = max(1, min(10, max_results))

    # Validate similarity score (handle string input from LLM)
    if isinstance(min_similarity_score, str):
        try:
            min_similarity_score = float(min_similarity_score)
        except ValueError:
            min_similarity_score = 0.0
    min_similarity_score = max(0.0, min(1.0, min_similarity_score))

    # Parse categories filter
    category_list = []
    if categories and categories.strip():
        category_list = [cat.strip().lower() for cat in categories.split(",")]
        valid_categories = {"product", "shipping", "return", "payment", "general"}
        category_list = [cat for cat in category_list if cat in valid_categories]

    # Perform search with filters
    results = vector_store.search_with_scores(
        query=query,
        k=max_results,
        filter_categories=category_list if category_list else None,
        score_threshold=min_similarity_score
    )

    if not results:
        filter_info = f" (filtered by: {', '.join(category_list)})" if category_list else ""
        score_info = f" with minimum score {min_similarity_score}" if min_similarity_score > 0 else ""
        return f"No relevant information found{filter_info}{score_info}.\n\nTry:\n- Broader search terms\n- Lower similarity threshold\n- Removing category filters"

    # Format results with scores and metadata
    formatted_results = ["Vector Knowledge Base Search Results:\n"]
    formatted_results.append(f"Query: '{query}'\n")

    if category_list:
        formatted_results.append(f"Categories: {', '.join(category_list)}")
    if min_similarity_score > 0:
        formatted_results.append(f"Min Similarity: {min_similarity_score:.2f}")

    formatted_results.append(f"\nFound {len(results)} relevant result(s):\n")
    formatted_results.append("-" * 60)

    for i, (doc, score) in enumerate(results, 1):
        category = doc.metadata.get("category", "unknown")
        doc_type = doc.metadata.get("type", "unknown")

        # Visual indicators for relevance
        if score >= 0.7:
            relevance = "🎯 High"
        elif score >= 0.5:
            relevance = "✓ Medium"
        elif score >= 0.3:
            relevance = "~ Low"
        else:
            relevance = "? Very Low"

        formatted_results.append(f"\nResult #{i} | Relevance: {relevance} ({score:.3f})")
        formatted_results.append(f"Category: {category.title()} | Type: {doc_type}")
        formatted_results.append("-" * 60)
        formatted_results.append(doc.page_content.strip())
        formatted_results.append("-" * 60)

    return "\n".join(formatted_results)


@tool
def escalate_to_human(reason: str, customer_message: str) -> str:
    """
    Escalate the conversation to a human support agent.
    
    WHAT IT DOES:
    Creates a support ticket and transfers the conversation to a human agent.
    Different escalation types get different response messages (e.g., frustrated
    customers get priority, complex issues get assigned to specialists).

    WHY IT'S IMPORTANT:
    Not all customer issues can be solved by an AI agent. This tool provides a
    graceful way to hand off to humans when:
    - Customer is upset (needs empathy and special handling)
    - Issue is too complex for automation
    - Customer explicitly requests human
    - Agent doesn't have the information needed
    
    HOW IT WORKS:
    1. Takes escalation reason and customer message
    2. Generates unique ticket ID
    3. Logs escalation (in production, would create ticket in help desk system)
    4. Returns appropriate message based on escalation type
    5. Different messages for frustrated vs complex vs explicit requests
    
    Use this tool when:
    - Customer is frustrated, angry, or dissatisfied
    - Issue is too complex for automated handling
    - Customer explicitly requests to speak with a human
    - You cannot find information needed to help
    - Issue requires manual intervention or special exceptions
    - Customer has been asking the same question multiple times
    
    Args:
        reason: Why escalation is needed (e.g., "customer_frustrated", "complex_issue", 
                "requires_manual_review", "explicit_request")
        customer_message: The most recent customer message that triggered escalation
    
    Returns:
        Escalation confirmation and next steps for the customer
    """
    # Generate support ticket (in production, this would create a ticket in your system)
    ticket_id = f"TICKET-{abs(hash(customer_message + reason)) % 10000:04d}"
    timestamp = datetime.now().strftime("%I:%M %p")
    
    # Log escalation for monitoring (in production, send to logging system)
    escalation_log = {
        "ticket_id": ticket_id,
        "timestamp": timestamp,
        "reason": reason,
        "customer_message": customer_message[:200],  # Truncate for logging
    }
    print(f"🚨 ESCALATION CREATED: {json.dumps(escalation_log, indent=2)}")
    
    # Different messages based on reason
    if "frustrated" in reason.lower() or "angry" in reason.lower():
        return f"""I completely understand your frustration, and I sincerely apologize for the inconvenience.

I've created priority support ticket {ticket_id} and notified our senior support team.
A specialist will reach out to you within 15 minutes to resolve this personally.

Your experience matters to us, and we're committed to making this right.

Is there anything I can help with in the meantime?"""
    
    elif "complex" in reason.lower():
        return f"""This situation requires specialized attention to ensure we handle it correctly.

I've created support ticket {ticket_id} and assigned it to our expert team.
They'll review your case and contact you within 30 minutes with a solution.

You'll receive an email confirmation with your ticket number shortly.

Can I help you with anything else while you wait?"""
    
    else:
        return f"""I've connected you with our human support team.

Support Ticket: {ticket_id}
Status: Assigned to agent
Expected Response: Within 15 minutes

A customer support specialist will reach out to you shortly via your preferred contact method.

Is there anything else I can assist you with?"""


# Export all tools as a list for easy import
# WHAT: List of all available tools that the agent can use
# WHY: This list is imported by agent.py and bound to the LLM. The LLM reads
#      this list to know what actions it can take. You can comment out tools
#      to disable them, or add new tools to give the agent more capabilities.
#      Note: search_knowledge_base is commented out in favor of search_vector_knowledge_base
#      which is more powerful
tools = [
    # search_knowledge_base,  # Basic search - using vector search instead
    search_vector_knowledge_base,  # Advanced semantic search with similarity scores
    get_order_status,  # Check order tracking and delivery
    initiate_return,  # Start return process for orders
    check_product_availability,  # Check if products are in stock
    escalate_to_human,  # Transfer to human support agent
]
