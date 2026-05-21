"""
cart_service.py — Cart management (session-based)
Author: Salma Hani  |  ID: 120210255
"""

from models import MenuItem


def get_cart(session_obj: dict) -> list:
    return session_obj.get("cart", [])


def clear_cart(session_obj: dict):
    session_obj["cart"] = []


def add_to_cart(session_obj: dict, item_id: int, quantity: int, note: str, menu_item: MenuItem) -> list:
    """
    Add or update item in session cart.
    Price is ALWAYS taken from the menu_item DB object — never from caller input.
    """
    cart = session_obj.get("cart", [])

    for entry in cart:
        if entry["item_id"] == item_id:
            new_qty = entry["quantity"] + quantity
            if new_qty > 20:
                raise ValueError("Maximum quantity per item is 20")
            entry["quantity"] = new_qty
            session_obj["cart"] = cart
            return cart

    cart.append({
        "item_id": item_id,
        "name": menu_item.name,
        "price": menu_item.price,   # server-side price only
        "quantity": quantity,
        "note": note,
    })
    session_obj["cart"] = cart
    return cart


def validate_cart_items(cart: list) -> list[str]:
    """
    Re-check every cart item against the DB at checkout time.
    Returns list of unavailable item names. Empty list means all OK.
    """
    unavailable = []
    for entry in cart:
        item = MenuItem.query.get(entry["item_id"])
        if not item or not item.available:
            unavailable.append(entry["name"])
    return unavailable
