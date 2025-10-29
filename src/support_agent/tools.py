"""Customer support tools using @tool decorator."""

from langchain_core.tools import tool
from datetime import datetime, timedelta
import json
from pathlib import Path
from .vector_store import get_vector_store


# Mock data - in production, replace with real database/API calls
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
    """Search the store's knowledge base for information about policies, products, and FAQ.

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
    """Look up the current status and tracking information for a customer's order.
    
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
    """Start the return process for a customer's order.
    
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
    """Check if a product is currently in stock and available for purchase.
    
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
def escalate_to_human(reason: str, customer_message: str) -> str:
    """Escalate the conversation to a human support agent.
    
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
tools = [
    search_knowledge_base,
    get_order_status,
    initiate_return,
    check_product_availability,
    escalate_to_human,
]
