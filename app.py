"""
app.py — Customer Ordering System
Author: Salma Hani  |  ID: 120210255
Flask application entry point with all routes.
"""

from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

from db import db
from models import MenuItem, Order
from order_service import calculate_total, create_order, check_idempotency
from cart_service import add_to_cart, get_cart, clear_cart, validate_cart_items
from payment_service import charge_card, PaymentError
from auth_service import require_session, validate_session_binding

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///orders.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

db.init_app(app)


@app.before_request
def make_session_permanent():
    session.permanent = True


# ── UI Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("order.html")


@app.route("/track/<order_id>")
def track(order_id):
    return render_template("order.html", order_id=order_id)


# ── API: Menu ──────────────────────────────────────────────────────────────

@app.route("/api/menu", methods=["GET"])
def get_menu():
    """
    Returns all menu items grouped by category.
    Internal: DB query and caching are hidden from caller.
    """
    items = MenuItem.query.filter_by(available=True).all()
    categories = {}
    for item in items:
        cat = item.category or "Other"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "available": item.available,
        })

    return jsonify({
        "categories": [
            {"name": k, "items": v} for k, v in categories.items()
        ]
    })


# ── API: Cart ──────────────────────────────────────────────────────────────

@app.route("/api/cart/add", methods=["POST"])
@require_session
def cart_add():
    """Add an item to the session cart."""
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)
    note = data.get("note", "")

    if not isinstance(quantity, int) or not (1 <= quantity <= 20):
        return jsonify({"error": "Quantity must be between 1 and 20.", "code": "INVALID_QUANTITY"}), 400

    menu_item = MenuItem.query.get(item_id)
    if not menu_item:
        return jsonify({"error": "Item not found.", "code": "NOT_FOUND"}), 404
    if not menu_item.available:
        return jsonify({"error": f"'{menu_item.name}' is currently unavailable.", "code": "ITEM_UNAVAILABLE"}), 409

    cart = add_to_cart(session, item_id, quantity, note, menu_item)
    return jsonify({"cart": cart, "total": calculate_total(cart)})

@app.route("/api/cart/remove", methods=["POST"])
@require_session
def cart_remove():
    """Remove an item from the session cart."""

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")

    if "cart" not in session:
        return jsonify({
            "error": "Cart is empty."
        }), 400

    updated_cart = []

    for item in session["cart"]:

        # keep all items except the removed one
        if item["item_id"] != item_id:
            updated_cart.append(item)

    session["cart"] = updated_cart
    session.modified = True

    return jsonify({
        "cart": updated_cart,
        "total": calculate_total(updated_cart)
    })


@app.route("/api/cart", methods=["GET"])
@require_session
def cart_view():
    cart = get_cart(session)
    return jsonify({"cart": cart, "total": calculate_total(cart) if cart else 0.0})


@app.route("/api/cart/clear", methods=["DELETE"])
@require_session
def cart_clear():
    clear_cart(session)
    return jsonify({"message": "Cart cleared."})


# ── API: Checkout ──────────────────────────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
@require_session
def checkout():
    """
    Validate cart, charge card, create order.
    Price is NEVER accepted from the client — always fetched from DB.
    """
    data = request.get_json(silent=True) or {}
    payment_token = data.get("payment_token")
    request_id = data.get("request_id")

    if not payment_token or not request_id:
        return jsonify({"error": "Missing payment_token or request_id.", "code": "BAD_REQUEST"}), 400

    # Idempotency check
    if check_idempotency(request_id):
        return jsonify({"error": "Duplicate request.", "code": "DUPLICATE_REQUEST"}), 409

    cart = get_cart(session)
    if not cart:
        return jsonify({"error": "Your cart is empty.", "code": "EMPTY_CART"}), 400

    # Re-validate all items against DB at checkout time
    unavailable = validate_cart_items(cart)
    if unavailable:
        return jsonify({
            "error": "Some items are no longer available.",
            "code": "ITEM_UNAVAILABLE",
            "items": unavailable
        }), 409

    total = calculate_total(cart)

    try:
        charge_id = charge_card(payment_token, total)
    except PaymentError as e:
        return jsonify({"error": str(e), "code": "PAYMENT_FAILED"}), 402

    order = create_order(session, cart, total, charge_id, request_id)
    clear_cart(session)

    return jsonify({
        "order_id": order.order_id,
        "status": order.status,
        "total": total
    }), 201


# ── API: Order Status ──────────────────────────────────────────────────────

@app.route("/api/order/<order_id>/status", methods=["GET"])
@require_session
def order_status(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found.", "code": "NOT_FOUND"}), 404
    if order.session_id != session.get("session_id"):
        return jsonify({"error": "Access denied.", "code": "FORBIDDEN"}), 403
    return jsonify({"order_id": order.order_id, "status": order.status})


# ── Dev: Seed DB ───────────────────────────────────────────────────────────

@app.route("/dev/seed", methods=["POST"])
def seed():
    """Development only: seed menu items."""
    db.drop_all()
    db.create_all()
    items = [
        MenuItem(name="Chicken Burger", description="Crispy fried chicken with lettuce and pickles", price=85.0, category="Burgers", available=True),
        MenuItem(name="Beef Burger", description="100% beef patty with caramelized onions", price=110.0, category="Burgers", available=True),
        MenuItem(name="Grilled Salmon", description="Atlantic salmon with herbs and lemon butter", price=195.0, category="Mains", available=False),
        MenuItem(name="Caesar Salad", description="Romaine, croutons, parmesan, Caesar dressing", price=75.0, category="Salads", available=True),
        MenuItem(name="Margherita Pizza", description="Tomato sauce, mozzarella, fresh basil", price=120.0, category="Pizza", available=True),
        MenuItem(name="Diet Pepsi", description="330ml can", price=25.0, category="Drinks", available=True),
        MenuItem(name="Fresh Orange Juice", description="Freshly squeezed, 400ml", price=45.0, category="Drinks", available=True),
        MenuItem(name="Chocolate Lava Cake", description="Warm chocolate cake with vanilla ice cream", price=65.0, category="Desserts", available=True),
    ]
    db.session.add_all(items)
    db.session.commit()
    return jsonify({"message": "Seeded successfully."})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
