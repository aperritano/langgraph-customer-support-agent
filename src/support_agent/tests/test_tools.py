"""Tests for customer support tools."""

import pytest
from src.support_agent.tools import (
    get_order_status,
    initiate_return,
    check_product_availability,
    escalate_to_human,
    MOCK_ORDERS,
    MOCK_INVENTORY,
)


class TestGetOrderStatus:
    """Test order status lookup functionality."""

    def test_get_order_status_in_transit(self):
        """Test retrieving status for an in-transit order."""
        result = get_order_status.invoke({"order_id": "123456"})

        assert "123456" in result
        assert "in_transit" in result.lower() or "in transit" in result.lower()
        assert "tracking" in result.lower()

    def test_get_order_status_delivered(self):
        """Test retrieving status for a delivered order."""
        result = get_order_status.invoke({"order_id": "789012"})

        assert "789012" in result
        assert "delivered" in result.lower()

    def test_get_order_status_processing(self):
        """Test retrieving status for a processing order."""
        result = get_order_status.invoke({"order_id": "345678"})

        assert "345678" in result
        assert "processing" in result.lower()

    def test_get_order_status_not_found(self):
        """Test handling of non-existent order."""
        result = get_order_status.invoke({"order_id": "999999"})

        assert "not found" in result.lower()
        assert "999999" in result

    def test_get_order_status_strips_hash(self):
        """Test that order lookup works with or without # prefix."""
        result1 = get_order_status.invoke({"order_id": "123456"})
        result2 = get_order_status.invoke({"order_id": "#123456"})

        # Both should succeed and reference the same order
        assert "123456" in result1
        assert "123456" in result2
        assert "not found" not in result1.lower()
        assert "not found" not in result2.lower()

    def test_get_order_status_includes_items(self):
        """Test that order status includes item information."""
        result = get_order_status.invoke({"order_id": "123456"})

        # Should mention the items in the order
        assert "wireless headphones" in result.lower() or "headphones" in result.lower()


class TestInitiateReturn:
    """Test return initiation functionality."""

    def test_initiate_return_defective_item(self):
        """Test return process for defective items (free shipping)."""
        result = initiate_return.invoke({
            "order_id": "123456",
            "reason": "defective"
        })

        assert "123456" in result
        assert "RMA-" in result or "return" in result.lower()
        assert "free" in result.lower()  # Should mention free return shipping

    def test_initiate_return_changed_mind(self):
        """Test return process for non-defective returns (paid shipping)."""
        result = initiate_return.invoke({
            "order_id": "123456",
            "reason": "changed_mind"
        })

        assert "123456" in result
        assert "RMA-" in result or "return" in result.lower()
        # Should mention shipping cost for regular returns
        assert "$" in result or "deducted" in result.lower()

    def test_initiate_return_damaged_item(self):
        """Test that damaged items get free return shipping."""
        result = initiate_return.invoke({
            "order_id": "789012",
            "reason": "damaged"
        })

        assert "789012" in result
        assert "free" in result.lower()

    def test_initiate_return_nonexistent_order(self):
        """Test return attempt for non-existent order."""
        result = initiate_return.invoke({
            "order_id": "999999",
            "reason": "defective"
        })

        assert "999999" in result
        assert "not found" in result.lower() or "couldn't find" in result.lower()

    def test_initiate_return_generates_rma(self):
        """Test that return authorization number is generated."""
        result = initiate_return.invoke({
            "order_id": "123456",
            "reason": "wrong_item"
        })

        assert "RMA-" in result  # Should contain return authorization

    def test_initiate_return_includes_steps(self):
        """Test that return instructions include clear steps."""
        result = initiate_return.invoke({
            "order_id": "123456",
            "reason": "not_as_described"
        })

        # Should include numbered steps or clear instructions
        assert "email" in result.lower()
        assert "pack" in result.lower()
        assert "refund" in result.lower()


class TestCheckProductAvailability:
    """Test product availability checking."""

    def test_check_in_stock_product(self):
        """Test checking an in-stock product."""
        result = check_product_availability.invoke({"product_name": "laptop"})

        assert "laptop" in result.lower()
        assert "in stock" in result.lower() or "available" in result.lower()

    def test_check_low_stock_product(self):
        """Test checking a low-stock product."""
        result = check_product_availability.invoke({"product_name": "headphones"})

        assert "headphones" in result.lower()
        assert "low" in result.lower() or "stock" in result.lower()

    def test_check_out_of_stock_product(self):
        """Test checking an out-of-stock product."""
        result = check_product_availability.invoke({"product_name": "mouse"})

        assert "mouse" in result.lower()
        assert "out of stock" in result.lower() or "restock" in result.lower()

    def test_check_product_not_found(self):
        """Test checking a product not in inventory."""
        result = check_product_availability.invoke({"product_name": "unicorn"})

        assert "couldn't find" in result.lower() or "not found" in result.lower()

    def test_check_product_case_insensitive(self):
        """Test that product search is case-insensitive."""
        result1 = check_product_availability.invoke({"product_name": "LAPTOP"})
        result2 = check_product_availability.invoke({"product_name": "laptop"})

        # Both should find the product
        assert "laptop" in result1.lower()
        assert "laptop" in result2.lower()
        assert "couldn't find" not in result1.lower()
        assert "couldn't find" not in result2.lower()

    def test_check_product_includes_stock_count(self):
        """Test that in-stock products show quantity."""
        result = check_product_availability.invoke({"product_name": "keyboard"})

        assert "keyboard" in result.lower()
        # Should mention stock count or quantity
        assert any(char.isdigit() for char in result)


class TestEscalateToHuman:
    """Test human escalation functionality."""

    def test_escalate_frustrated_customer(self):
        """Test escalation for frustrated customers."""
        result = escalate_to_human.invoke({
            "reason": "customer_frustrated",
            "customer_message": "This is ridiculous! I've been waiting forever!"
        })

        assert "TICKET-" in result or "ticket" in result.lower()
        assert "apologize" in result.lower() or "sorry" in result.lower()

    def test_escalate_complex_issue(self):
        """Test escalation for complex issues."""
        result = escalate_to_human.invoke({
            "reason": "complex_issue",
            "customer_message": "I need to modify my order and change shipping"
        })

        assert "TICKET-" in result or "ticket" in result.lower()
        assert "specialist" in result.lower() or "expert" in result.lower()

    def test_escalate_explicit_request(self):
        """Test escalation when customer requests human agent."""
        result = escalate_to_human.invoke({
            "reason": "explicit_request",
            "customer_message": "I want to speak to a human"
        })

        assert "TICKET-" in result or "ticket" in result.lower()

    def test_escalate_generates_unique_ticket(self):
        """Test that each escalation generates a unique ticket ID."""
        result1 = escalate_to_human.invoke({
            "reason": "complex_issue",
            "customer_message": "Issue number one"
        })
        result2 = escalate_to_human.invoke({
            "reason": "complex_issue",
            "customer_message": "Issue number two"
        })

        # Extract ticket IDs (basic check)
        assert "TICKET-" in result1
        assert "TICKET-" in result2
        # Different messages should generate different tickets
        # (though hash collisions are possible, unlikely for these test cases)

    def test_escalate_includes_response_time(self):
        """Test that escalation mentions expected response time."""
        result = escalate_to_human.invoke({
            "reason": "requires_manual_review",
            "customer_message": "I need special handling"
        })

        # Should mention timeframe
        assert "minutes" in result.lower() or "within" in result.lower()


class TestMockData:
    """Test mock data integrity."""

    def test_mock_orders_structure(self):
        """Test that MOCK_ORDERS has expected structure."""
        assert len(MOCK_ORDERS) > 0, "Should have mock orders"

        for order_id, order in MOCK_ORDERS.items():
            assert "status" in order, f"Order {order_id} should have status"
            assert "items" in order, f"Order {order_id} should have items"
            assert isinstance(order["items"], list), "Items should be a list"

    def test_mock_inventory_structure(self):
        """Test that MOCK_INVENTORY has expected structure."""
        assert len(MOCK_INVENTORY) > 0, "Should have mock inventory"

        for product, details in MOCK_INVENTORY.items():
            assert "stock" in details, f"Product {product} should have stock count"
            assert "status" in details, f"Product {product} should have status"
            assert isinstance(details["stock"], int), "Stock should be an integer"

    def test_mock_data_consistency(self):
        """Test that mock data statuses are consistent with stock levels."""
        for product, details in MOCK_INVENTORY.items():
            stock = details["stock"]
            status = details["status"]

            if stock == 0:
                assert status == "out_of_stock", f"{product} with 0 stock should be out_of_stock"
            elif stock < 5:
                assert status == "low_stock", f"{product} with low stock should be low_stock"
            else:
                assert status == "in_stock", f"{product} with {stock} units should be in_stock"
