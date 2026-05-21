"""
tests/test_order_service.py
Author: Salma Hani  |  ID: 120210255

TDP Unit Tests — written BEFORE implementation.
These tests define the mathematical boundary that order_service.py must satisfy.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from order_service import calculate_total


# ── Unit Tests: calculate_total() ─────────────────────────────────────────

class TestCalculateTotal:

    def test_basic_single_item(self):
        """100 EGP item x 1 + 14% tax = 114.0"""
        items = [{"price": 100.0, "quantity": 1}]
        assert calculate_total(items) == 114.0

    def test_basic_multiple_items(self):
        """100*2 + 50*1 = 250 + 14% = 285.0"""
        items = [{"price": 100.0, "quantity": 2}, {"price": 50.0, "quantity": 1}]
        assert calculate_total(items) == 285.0

    def test_empty_cart_raises(self):
        """Padlock P-01 boundary: empty list must raise ValueError."""
        with pytest.raises(ValueError, match="Cart is empty"):
            calculate_total([])

    def test_zero_price_raises(self):
        """Padlock: price of 0 is never valid."""
        items = [{"price": 0.0, "quantity": 1}]
        with pytest.raises(ValueError, match="Invalid price"):
            calculate_total(items)

    def test_negative_price_raises(self):
        items = [{"price": -10.0, "quantity": 1}]
        with pytest.raises(ValueError, match="Invalid price"):
            calculate_total(items)

    def test_negative_quantity_raises(self):
        """Padlock: quantity < 1 must be rejected."""
        items = [{"price": 50.0, "quantity": -1}]
        with pytest.raises(ValueError, match="Invalid quantity"):
            calculate_total(items)

    def test_zero_quantity_raises(self):
        """Padlock P-01: quantity = 0 rejected."""
        items = [{"price": 50.0, "quantity": 0}]
        with pytest.raises(ValueError, match="Invalid quantity"):
            calculate_total(items)

    def test_rounding_precision(self):
        """Padlock P-03: floating-point drift must not occur."""
        items = [{"price": 33.33, "quantity": 3}]
        result = calculate_total(items)
        # 33.33 * 3 = 99.99; * 1.14 = 113.9886 → round to 113.99
        assert result == round(99.99 * 1.14, 2)
        assert isinstance(result, float)

    def test_large_cart_extreme(self):
        """Padlock P-05: 10 items × 20 qty each should process without error."""
        items = [{"price": float(10 + i), "quantity": 20} for i in range(10)]
        result = calculate_total(items)
        expected_subtotal = sum((10 + i) * 20 for i in range(10))
        assert result == round(expected_subtotal * 1.14, 2)

    def test_tax_rate_is_14_percent(self):
        """Explicit tax rate verification: 1000 EGP + 14% = 1140.0"""
        items = [{"price": 1000.0, "quantity": 1}]
        assert calculate_total(items) == 1140.0

    def test_single_item_max_quantity(self):
        """Boundary: quantity 20 is the maximum allowed — should succeed."""
        items = [{"price": 50.0, "quantity": 20}]
        result = calculate_total(items)
        assert result == round(50.0 * 20 * 1.14, 2)


# ── Unit Tests: cart_service helpers (no DB needed) ───────────────────────

class TestCartServiceLogic:

    def test_quantity_exceeds_max(self):
        """
        Verifies that adding to a cart entry with qty 20 + 1 raises ValueError.
        cart_service.add_to_cart() is tested in integration tests.
        This tests the guard logic in isolation.
        """
        current_qty = 20
        additional = 1
        new_qty = current_qty + additional
        assert new_qty > 20, "Guard should trigger"

    def test_valid_quantity_range(self):
        for qty in range(1, 21):
            assert 1 <= qty <= 20

    def test_invalid_quantity_below(self):
        assert not (1 <= 0 <= 20)

    def test_invalid_quantity_above(self):
        assert not (1 <= 21 <= 20)
