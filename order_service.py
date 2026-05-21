"""
order_service.py — Order business logic
Author: Salma Hani  |  ID: 120210255

calculate_total() is the core function validated by TDP unit tests.
The implementation was written to satisfy test_order_service.py exactly.
"""

from db import db
from models import Order, OrderItem
from datetime import datetime, timedelta
import uuid


TAX_RATE = 0.14


def calculate_total(items: list) -> float:
    """
    Calculate cart total including 14% tax.

    Boundary constraints (from TDP padlocks):
    - items must not be empty        → raises ValueError('Cart is empty')
    - each price must be > 0         → raises ValueError('Invalid price')
    - each quantity must be >= 1     → raises ValueError('Invalid quantity')

    Returns total rounded to 2 decimal places.
    """
    if not items:
        raise ValueError("Cart is empty")

    subtotal = 0.0
    for item in items:
        if item["price"] <= 0:
            raise ValueError("Invalid price")
        if item["quantity"] < 1:
            raise ValueError("Invalid quantity")
        subtotal += item["price"] * item["quantity"]

    return round(subtotal * (1 + TAX_RATE), 2)


def check_idempotency(request_id: str) -> bool:
    """
    Return True if this request_id was already processed within the last 60 seconds.
    Prevents duplicate orders on double-submit.
    """
    cutoff = datetime.utcnow() - timedelta(seconds=60)
    existing = Order.query.filter(
        Order.request_id == request_id,
        Order.created_at >= cutoff
    ).first()
    return existing is not None


def create_order(session_obj, cart: list, total: float, charge_id: str, request_id: str) -> Order:
    """
    Persist a new order and its items to the database.
    Session ID is bound to the order for ownership validation.
    """
    order = Order(
        order_id=f"ORD-{uuid.uuid4().hex[:6].upper()}",
        session_id=session_obj.get("session_id", "unknown"),
        total=total,
        status="Received",
        charge_id=charge_id,
        request_id=request_id,
    )
    db.session.add(order)
    db.session.flush()  # Get order.id before adding items

    for item in cart:
        db.session.add(OrderItem(
            order_id=order.id,
            menu_item_id=item["item_id"],
            name=item["name"],
            unit_price=item["price"],
            quantity=item["quantity"],
            note=item.get("note", ""),
        ))

    db.session.commit()
    return order
