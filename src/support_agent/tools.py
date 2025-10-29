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
from .prompts import INITIAL_GREETING


# Mock data - in production, replace with real database/API calls
# WHAT: Sample order and inventory data for testing/demo purposes
# WHY: In a real system, these would be database queries or API calls to your
#      order management system and inventory system. For demo/development, we use
#      hardcoded data so the tools work without setting up external services.
MOCK_ORDERS = {
    # Processing orders (pending shipment)
    "345678": {
        "status": "processing",
        "expected_ship": (datetime.now() + timedelta(days=1)).strftime("%b %d, %Y"),
        "items": ["Mechanical Keyboard", "Mouse Pad"],
    },
    "234567": {
        "status": "processing",
        "expected_ship": (datetime.now() + timedelta(days=2)).strftime("%b %d, %Y"),
        "items": ["Gaming Mouse", "RGB Keyboard"],
    },
    "456789": {
        "status": "processing",
        "expected_ship": (datetime.now() + timedelta(hours=12)).strftime("%b %d, %Y"),
        "items": ["USB-C Hub", "Ethernet Adapter", "HDMI Cable"],
    },
    "567890": {
        "status": "processing",
        "expected_ship": (datetime.now() + timedelta(days=3)).strftime("%b %d, %Y"),
        "items": ["External Hard Drive 2TB"],
    },
    # In transit orders (shipped)
    "123456": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=2)).strftime("%b %d, %Y"),
        "tracking": "1Z999AA10123456784",
        "items": ["Wireless Headphones", "USB Cable"],
    },
    "678901": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=1)).strftime("%b %d, %Y"),
        "tracking": "1Z888BB20234567895",
        "items": ["Webcam 1080p", "Microphone"],
    },
    "789012": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=0)).strftime("%b %d, %Y"),
        "items": ["Monitor Stand", "Desk Mat"],
    },
    "890123": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=1)).strftime("%b %d, %Y"),
        "tracking": "1Z666DD40456789017",
        "items": ["Laptop Cooling Pad", "USB-C to USB-A Adapter"],
    },
    "901234": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=4)).strftime("%b %d, %Y"),
        "tracking": "1Z555EE50567890128",
        "items": ["Docking Station", "External SSD 1TB"],
    },
    "112233": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(hours=18)).strftime("%b %d, %Y"),
        "tracking": "1Z444FF60678901239",
        "items": ["Wireless Charger", "Phone Stand"],
    },
    # Delivered orders (recent)
    "223344": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=1)).strftime("%b %d, %Y"),
        "items": ["Monitor 27\"", "HDMI Cable"],
    },
    "334455": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=2)).strftime("%b %d, %Y"),
        "items": ["Desk Lamp", "Cable Management Kit"],
    },
    "445566": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=3)).strftime("%b %d, %Y"),
        "items": ["Laptop Stand"],
    },
    "556677": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=5)).strftime("%b %d, %Y"),
        "items": ["Ergonomic Mouse", "Wrist Rest"],
    },
    "667788": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=7)).strftime("%b %d, %Y"),
        "items": ["Wireless Keyboard", "Mouse Pad"],
    },
    # Delivered orders (older - may be eligible for return)
    "778899": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=10)).strftime("%b %d, %Y"),
        "items": ["USB-C Cable 6ft", "Power Bank"],
    },
    "889900": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=15)).strftime("%b %d, %Y"),
        "items": ["Bluetooth Speaker", "Car Mount"],
    },
    "990011": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=20)).strftime("%b %d, %Y"),
        "items": ["Smart Watch Band", "Screen Protector"],
    },
    "001122": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=25)).strftime("%b %d, %Y"),
        "items": ["Laptop Sleeve", "Keyboard Cover"],
    },
    # Multi-item orders
    "111222": {
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=2)).strftime("%b %d, %Y"),
        "tracking": "1Z333GG70789012340",
        "items": ["Gaming Headset", "Mouse Bungee", "Extended Mouse Pad", "Cable Clips"],
    },
    "222333": {
        "status": "delivered",
        "delivered_date": (datetime.now() - timedelta(days=4)).strftime("%b %d, %Y"),
        "items": ["Standing Desk Converter", "Monitor Arm", "Desk Organizer"],
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

    return f"""🔍 Knowledge Base Search Results
    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: {category.title()}

{results}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Need more information? Try searching with different terms or ask me a specific question."""


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
        return f"""❌ Order Not Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Order #{order_id} was not found in our system.

Please verify the order number and try again. Order numbers are typically 6 digits 
and can be found in your confirmation email.

💡 If you continue to have trouble, I can escalate this to a human agent who can 
   help locate your order."""
    
    # Format response based on status
    if order["status"] == "in_transit":
        return f"""📦 Order #{order_id} - In Transit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           Your order is on its way!
Expected Delivery: {order['expected_delivery']}
Tracking Number:  {order['tracking']}

Items:
{chr(10).join('  • ' + item for item in order['items'])}

🔗 Track Your Package:
   https://track.example.com/{order['tracking']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    elif order["status"] == "delivered":
        return f"""✅ Order #{order_id} - Delivered

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:    Successfully delivered
Delivered: {order['delivered_date']}

Items:
{chr(10).join('  • ' + item for item in order['items'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 If you haven't received your package or there are any issues, please let me 
   know and I can help!"""
    
    elif order["status"] == "processing":
        return f"""⏳ Order #{order_id} - Processing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           Your order is being prepared for shipment
Expected Ship Date: {order['expected_ship']}

Items:
{chr(10).join('  • ' + item for item in order['items'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 You'll receive a tracking number via email as soon as your order ships. 
   Thanks for your patience!"""
    
    return f"""📋 Order #{order_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: {order['status'].replace('_', ' ').title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


@tool
def list_orders(status_filter: str = "all") -> str:
    """
    List orders and filter them by status (e.g., show all orders that haven't shipped).
    
    WHAT IT DOES:
    Queries the order management system to list orders, optionally filtered by status.
    This allows the agent to answer questions like "show me all orders that haven't shipped"
    or "what orders are pending?"
    
    WHY IT'S IMPORTANT:
    Customers may ask about multiple orders at once, or want to see all orders in a
    particular state (e.g., all unshipped orders). This tool provides visibility into
    order collections, not just individual order lookups. Without this, the agent can
    only check one order at a time, which doesn't work for queries about multiple orders.
    
    HOW IT WORKS:
    1. Takes optional status filter (e.g., "processing", "in_transit", "delivered", "all")
    2. Filters MOCK_ORDERS by status (in production, would query database/API)
    3. Returns formatted list of matching orders with their details
    
    Use this tool when customers ask about:
    - Show me all orders that haven't shipped yet
    - List all my pending orders
    - What orders are still processing?
    - Show me all my orders
    - Orders that haven't been delivered
    
    Args:
        status_filter: Filter orders by status. Options:
                      - "processing": Orders that haven't shipped yet (being prepared)
                      - "in_transit": Orders that have shipped and are en route
                      - "delivered": Orders that have been delivered
                      - "not_shipped": Orders that haven't shipped (same as "processing")
                      - "shipped": Orders that have shipped (includes "in_transit" and "delivered")
                      - "all": Show all orders regardless of status (default)
    
    Returns:
        Formatted list of orders matching the status filter
    """
    # Normalize status filter
    status_filter_lower = status_filter.lower().strip()
    
    # Map aliases to actual status values
    status_mapping = {
        "not_shipped": "processing",
        "pending": "processing",
        "unshipped": "processing",
        "shipped": None,  # Special case: includes both in_transit and delivered
    }
    
    # Get target status(es)
    target_statuses = []
    if status_filter_lower == "all":
        # Return all orders
        target_statuses = None
    elif status_filter_lower in status_mapping:
        mapped = status_mapping[status_filter_lower]
        if mapped is None:
            # "shipped" means both in_transit and delivered
            target_statuses = ["in_transit", "delivered"]
        else:
            target_statuses = [mapped]
    else:
        # Use filter as-is (processing, in_transit, delivered)
        target_statuses = [status_filter_lower]
    
    # Filter orders
    matching_orders = []
    for order_id, order in MOCK_ORDERS.items():
        if target_statuses is None or order["status"] in target_statuses:
            matching_orders.append((order_id, order))
    
    if not matching_orders:
        filter_desc = f"with status '{status_filter}'" if status_filter_lower != "all" else ""
        return f"""❌ No Orders Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No orders found {filter_desc}.

💡 Would you like me to:
   • Check a specific order number
   • Try a different status filter

Available filters: processing, in_transit, delivered, not_shipped, shipped, all"""
    
    # Format results with improved readability
    results = []
    
    # Header
    if status_filter_lower == "all":
        results.append(f"📋 All Orders ({len(matching_orders)} total)")
    else:
        filter_desc = status_filter.replace("_", " ").title()
        if status_filter_lower == "not_shipped":
            filter_desc = "Not Shipped"
        results.append(f"📋 {filter_desc} Orders ({len(matching_orders)} found)")
    
    results.append("")
    results.append("━" * 70)
    results.append("")
    
    # Group by status for better readability
    by_status = {"processing": [], "in_transit": [], "delivered": []}
    for order_id, order in matching_orders:
        by_status[order["status"]].append((order_id, order))
    
    # Display by status category with clean formatting
    for status_idx, (status, orders) in enumerate(by_status.items()):
        if not orders:
            continue
        
        # Status header
        if status == "processing":
            status_header = f"⏳ Processing ({len(orders)} order{'s' if len(orders) != 1 else ''})"
        elif status == "in_transit":
            status_header = f"📦 In Transit ({len(orders)} order{'s' if len(orders) != 1 else ''})"
        elif status == "delivered":
            status_header = f"✅ Delivered ({len(orders)} order{'s' if len(orders) != 1 else ''})"
        
        results.append(status_header)
        results.append("")
        
        # Orders in this status
        for order_idx, (order_id, order) in enumerate(orders, 1):
            results.append(f"  ┌─ Order #{order_id}")
            
            if status == "processing":
                results.append(f"  │  Expected Ship: {order.get('expected_ship', 'TBD')}")
            elif status == "in_transit":
                results.append(f"  │  Expected Delivery: {order.get('expected_delivery', 'TBD')}")
                results.append(f"  │  Tracking: {order.get('tracking', 'N/A')}")
            elif status == "delivered":
                results.append(f"  │  Delivered: {order.get('delivered_date', 'TBD')}")
            
            # Items as a bullet list
            items_list = order['items']
            results.append(f"  │  Items: {items_list[0]}")
            for item in items_list[1:]:
                results.append(f"  │          {item}")
            
            # Close box or add separator
            if order_idx < len(orders):
                results.append(f"  └─")
                results.append("")
            else:
                results.append(f"  └─")
        
        # Add separator between status groups
        if status_idx < len([s for s in by_status.values() if s]) - 1:
            results.append("")
            results.append("─" * 70)
            results.append("")
    
    results.append("")
    results.append("━" * 70)
    results.append("")
    
    if matching_orders:
        results.append("💡 For detailed tracking, ask about a specific order number.")
    
    return "\n".join(results)


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
    4. Removes the order from the system (since it's being returned/refunded)
    5. Determines if return is free (defective/damaged) or paid (other reasons)
    6. Returns formatted instructions with RMA number and steps
    
    NOTE: Once a return is initiated, the order is removed from MOCK_ORDERS.
    In production, you would update the order status in your database instead.
    
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
        return f"""❌ Order Not Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I couldn't find order #{order_id}.

💡 Please verify the order number and try again."""
    
    # Generate return authorization (in production, this would create a database entry)
    return_id = f"RMA-{order_id}-{hash(reason) % 1000:03d}"
    
    # Store items list before removing order
    items_list = ', '.join(order['items'])
    
    # In tests and demo, avoid mutating global state. In production, you would
    # update order status in the database instead of deleting from memory.
    
    # Different process for defective items
    if "defect" in reason.lower() or "damaged" in reason.lower() or "broken" in reason.lower():
        return f"""🔄 Return Authorized - Order #{order_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return Authorization: {return_id}
Reason:               {reason.title()}
Items:                {items_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Since your item is defective/damaged, we'll make this easy:

┌─ Return Process ─────────────────────────────────────────────────────────────┐
│                                                                               │
│  1. ✅ FREE return shipping label will be emailed to you within 1 hour      │
│  2. 📦 Pack the item securely in any box                                     │
│  3. 📧 Print the label and attach it to the package                          │
│  4. 🚚 Drop off at any UPS location or schedule a pickup                     │
│  5. 💰 Full refund processed within 5-7 business days after we receive it    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

We apologize for the inconvenience! Is there anything else I can help with?"""
    
    else:
        return f"""🔄 Return Authorized - Order #{order_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return Authorization: {return_id}
Reason:               {reason.title()}
Items:                {items_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Here's how to return your order:

┌─ Return Process ─────────────────────────────────────────────────────────────┐
│                                                                               │
│  1. 📧 Return label will be emailed to you within 1 hour                      │
│     ($7.99 deducted from refund)                                            │
│  2. 📦 Pack the item in original packaging with all accessories and tags     │
│  3. 🏷️ Print the label and attach it to the package                          │
│  4. 🚚 Drop off at any UPS location                                          │
│  5. 💰 Refund processed within 5-7 business days after we receive it          │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

⚠️  Note: Items must be unused and in original condition for a full refund.

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
        return f"""❌ Product Not Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I couldn't find specific inventory information for "{product_name}".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Would you like me to:
   • Help you find something similar
   • Speak with a product specialist

You can also check our online catalog at: www.store.com/products"""
    
    # Format results
    results = ["📊 Product Availability\n"]
    results.append("━" * 70)
    results.append("")
    
    for product_idx, (product_key, details) in enumerate(found_products, 1):
        stock_count = details["stock"]
        status = details["status"]
        
        results.append(f"┌─ {product_key.title()}")
        
        if status == "in_stock":
            results.append(f"│  Status:    ✅ IN STOCK")
            results.append(f"│  Available: {stock_count} units")
            results.append(f"│")
            results.append(f"│  💡 Ready to ship within 1-2 business days!")
        elif status == "low_stock":
            results.append(f"│  Status:    ⚠️  LOW STOCK")
            results.append(f"│  Available: {stock_count} units remaining")
            results.append(f"│")
            results.append(f"│  💡 Order soon to avoid missing out!")
        elif status == "out_of_stock":
            restock = details.get("restock_date", "TBD")
            results.append(f"│  Status:    ❌ OUT OF STOCK")
            results.append(f"│  Restock:   Expected {restock}")
            results.append(f"│")
            results.append(f"│  💡 Would you like me to notify you when it's back in stock?")
        
        if product_idx < len(found_products):
            results.append(f"└─")
            results.append("")
        else:
            results.append(f"└─")
    
    results.append("")
    results.append("━" * 70)
    
    return "\n".join(results)


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
        return f"""❌ No Relevant Information Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No relevant information found{filter_info}{score_info}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Try:
   • Using broader search terms
   • Lowering the similarity threshold
   • Removing category filters

Would you like me to search again with different parameters?"""

    # Format results with scores and metadata
    formatted_results = ["🔍 Vector Knowledge Base Search Results\n"]
    formatted_results.append("━" * 70)
    formatted_results.append("")
    formatted_results.append(f"Query: '{query}'")
    formatted_results.append("")

    if category_list:
        formatted_results.append(f"Categories: {', '.join([c.title() for c in category_list])}")
    if min_similarity_score > 0:
        formatted_results.append(f"Min Similarity: {min_similarity_score:.2f}")

    formatted_results.append("")
    formatted_results.append(f"Found {len(results)} relevant result(s):")
    formatted_results.append("")
    formatted_results.append("━" * 70)
    formatted_results.append("")

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

        formatted_results.append(f"┌─ Result #{i}")
        formatted_results.append(f"│  Relevance: {relevance} ({score:.3f})")
        formatted_results.append(f"│  Category:  {category.title()}")
        formatted_results.append(f"│  Type:      {doc_type.title()}")
        formatted_results.append(f"├─")
        formatted_results.append(f"│  {doc.page_content.strip().replace(chr(10), chr(10) + '│  ')}")
        
        if i < len(results):
            formatted_results.append(f"└─")
            formatted_results.append("")
            formatted_results.append("─" * 70)
            formatted_results.append("")
        else:
            formatted_results.append(f"└─")

    formatted_results.append("")
    formatted_results.append("━" * 70)

    return "\n".join(formatted_results)


@tool
def send_greeting() -> str:
    """
    Send a welcome greeting message to the customer introducing the agent and available services.
    
    WHAT IT DOES:
    Returns a friendly greeting message that introduces the customer support agent, lists
    available capabilities, and mentions that customers can view policies. Use this when
    starting a new conversation or when the customer first connects.
    
    WHY IT'S IMPORTANT:
    Provides a welcoming first impression and sets expectations about what the agent can
    help with. Makes the experience feel personal and helps customers understand what
    they can ask for.
    
    WHEN TO USE:
    - At the start of a new conversation
    - When this is the first interaction with a customer
    - When the customer first connects to chat
    
    HOW IT WORKS:
    1. Returns a formatted greeting message
    2. Lists capabilities (order status, returns, policies, etc.)
    3. Mentions ability to view policies
    4. Invites customer to ask questions
    
    Use this tool when:
    - Customer first connects
    - This is the first message in the conversation
    - You want to provide a welcoming introduction
    
    Returns:
        Formatted greeting message introducing the agent and services
    """
    return INITIAL_GREETING


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
        return f"""👤 Escalated to Human Support - Priority

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I completely understand your frustration, and I sincerely apologize for the inconvenience.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Support Ticket:      {ticket_id}
Priority Level:      High
Status:              Assigned to Senior Support Team
Expected Response:   Within 15 minutes

A specialist will reach out to you within 15 minutes to resolve this personally.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your experience matters to us, and we're committed to making this right.

💡 Is there anything I can help with in the meantime?"""
    
    elif "complex" in reason.lower():
        return f"""👤 Escalated to Human Support - Expert Review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This situation requires specialized attention to ensure we handle it correctly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Support Ticket:      {ticket_id}
Priority Level:      Standard
Status:              Assigned to Expert Team
Expected Response:   Within 30 minutes

They'll review your case and contact you within 30 minutes with a solution.

You'll receive an email confirmation with your ticket number shortly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Can I help you with anything else while you wait?"""
    
    else:
        return f"""👤 Escalated to Human Support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I've connected you with our human support team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Support Ticket:      {ticket_id}
Status:              Assigned to agent
Expected Response:   Within 15 minutes

A customer support specialist will reach out to you shortly via your preferred 
contact method.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Is there anything else I can assist you with?"""


# Function descriptions in user-friendly format for the list_available_functions tool
# WHAT: Pre-defined descriptions of all tools for display to users
# WHY: This provides consistent, user-friendly descriptions when listing capabilities
FUNCTION_DESCRIPTIONS = {
    "search_vector_knowledge_base": {
        "name": "🔍 Search Knowledge Base",
        "description": "Search the store's knowledge base for information about policies, products, and frequently asked questions using semantic similarity search",
        "use_cases": [
            "Find return policy information",
            "Get shipping policy details",
            "Look up product information",
            "Find answers to FAQ questions"
        ]
    },
    "get_order_status": {
        "name": "📦 Check Order Status",
        "description": "Look up the current status and tracking information for a customer's order",
        "use_cases": [
            "Check where an order is",
            "Get tracking information",
            "See expected delivery dates",
            "Find out if an order has shipped"
        ]
    },
    "list_orders": {
        "name": "📋 List Orders",
        "description": "List orders and filter them by status (e.g., show all orders that haven't shipped)",
        "use_cases": [
            "Show all orders that haven't shipped yet",
            "List all pending orders",
            "Find orders by status",
            "See all orders in a particular state"
        ]
    },
    "initiate_return": {
        "name": "🔄 Initiate Return",
        "description": "Start the return process for a customer's order and provide return instructions",
        "use_cases": [
            "Process a return request",
            "Generate return authorization (RMA)",
            "Get return shipping labels",
            "Start refund process"
        ]
    },
    "check_product_availability": {
        "name": "📊 Check Product Availability",
        "description": "Check if a product is currently in stock and available for purchase",
        "use_cases": [
            "Check if a product is in stock",
            "See how many units are available",
            "Find out when out-of-stock items will be restocked",
            "Verify product availability before ordering"
        ]
    },
    "escalate_to_human": {
        "name": "👤 Escalate to Human Agent",
        "description": "Transfer the conversation to a human support agent for complex issues or when requested",
        "use_cases": [
            "Customer requests to speak with a human",
            "Issue is too complex for automated handling",
            "Customer is frustrated and needs special attention",
            "Manual intervention is required"
        ]
    },
    "list_available_functions": {
        "name": "📋 List Available Functions",
        "description": "Show all available functions and actions the agent can perform",
        "use_cases": [
            "Show what the agent can do",
            "List all available capabilities",
            "Understand what actions are possible"
        ]
    },
    "send_greeting": {
        "name": "👋 Send Greeting",
        "description": "Send a welcome greeting message introducing the agent and available services",
        "use_cases": [
            "Greet customer at the start of conversation",
            "Introduce agent capabilities",
            "Welcome new customer",
            "Provide initial greeting when first connecting"
        ]
    }
}


@tool
def list_available_functions() -> str:
    """
    List all available functions/actions that the agent can perform.
    
    WHAT IT DOES:
    Returns a formatted list of all tools/functions available to the agent, including
    their names, descriptions, and use cases. This helps customers understand what
    the agent can help with.
    
    WHY IT'S IMPORTANT:
    Customers may ask "what can you do?" or "what functions do you have?" This tool
    provides a clear, comprehensive answer about the agent's capabilities, helping
    customers understand how the agent can assist them.
    
    HOW IT WORKS:
    1. Uses pre-defined function descriptions
    2. Formats each tool's name and description
    3. Returns a user-friendly formatted list
    
    Use this tool when customers ask:
    - What can you do?
    - What functions are available?
    - What actions can you perform?
    - What tools do you have?
    - List your capabilities
    
    Returns:
        Formatted list of all available functions with descriptions
    """
    formatted_functions = ["🤖 Available Functions & Actions\n"]
    formatted_functions.append("=" * 70)
    formatted_functions.append("")
    
    # List of available tools (must match the tools list at the bottom of this file)
    # This order determines the display order
    tool_names = [
        "list_available_functions",
        "send_greeting",
        "search_vector_knowledge_base",
        "get_order_status",
        "list_orders",
        "initiate_return",
        "check_product_availability",
        "escalate_to_human",
    ]
    
    for i, tool_name in enumerate(tool_names, 1):
        if tool_name in FUNCTION_DESCRIPTIONS:
            info = FUNCTION_DESCRIPTIONS[tool_name]
            formatted_functions.append(f"{i}. {info['name']}")
            formatted_functions.append("")
            formatted_functions.append(f"   {info['description']}")
            formatted_functions.append("")
            formatted_functions.append(f"   When to use:")
            for use_case in info['use_cases']:
                formatted_functions.append(f"     • {use_case}")
            
            # Add separator between items (except last)
            if i < len(tool_names):
                formatted_functions.append("")
                formatted_functions.append("-" * 70)
                formatted_functions.append("")
        else:
            # Fallback for any tools not in descriptions dict
            formatted_functions.append(f"{i}. {tool_name}")
            if i < len(tool_names):
                formatted_functions.append("")
                formatted_functions.append("-" * 70)
                formatted_functions.append("")
    
    formatted_functions.append("")
    formatted_functions.append("=" * 70)
    formatted_functions.append("")
    formatted_functions.append("💡 Tip: Just ask me naturally what you need help with, and I'll use the appropriate function!")
    
    return "\n".join(formatted_functions)


# Export all tools as a list for easy import
# WHAT: List of all available tools that the agent can use
# WHY: This list is imported by agent.py and bound to the LLM. The LLM reads
#      this list to know what actions it can take. You can comment out tools
#      to disable them, or add new tools to give the agent more capabilities.
#      Note: search_knowledge_base is commented out in favor of search_vector_knowledge_base
#      which is more powerful
tools = [
    list_available_functions,  # List all available functions/actions
    send_greeting,  # Send welcome greeting to customer
    # search_knowledge_base,  # Basic search - using vector search instead
    search_vector_knowledge_base,  # Advanced semantic search with similarity scores
    get_order_status,  # Check order tracking and delivery
    list_orders,  # List and filter orders by status
    initiate_return,  # Start return process for orders
    check_product_availability,  # Check if products are in stock
    escalate_to_human,  # Transfer to human support agent
]
