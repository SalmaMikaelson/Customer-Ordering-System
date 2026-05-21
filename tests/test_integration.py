"""
tests/test_integration.py
Author: Salma Hani  |  ID: 120210255

Integration tests — Flask test client + SQLite in-memory DB.
Tests the full request/response cycle across routes, models, and services.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app as flask_app
from db import db as _db
from models import MenuItem


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["SECRET_KEY"] = "test-secret"
    flask_app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.app_context():
        _db.create_all()
        _seed_db()
        yield flask_app
        _db.drop_all()


def _seed_db():
    _db.session.add_all([
        MenuItem(id=1, name="Chicken Burger", price=85.0, category="Burgers", available=True),
        MenuItem(id=2, name="Diet Pepsi", price=25.0, category="Drinks", available=True),
        MenuItem(id=3, name="Grilled Salmon", price=195.0, category="Mains", available=False),
    ])
    _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Integration Tests ──────────────────────────────────────────────────────

class TestMenuEndpoint:

    def test_get_menu_returns_available_items_only(self, client):
        res = client.get("/api/menu")
        assert res.status_code == 200
        data = res.get_json()
        all_items = [i for cat in data["categories"] for i in cat["items"]]
        names = [i["name"] for i in all_items]
        assert "Chicken Burger" in names
        assert "Grilled Salmon" not in names  # unavailable, excluded

    def test_menu_items_have_no_internal_fields(self, client):
        """API contract: internal fields must not leak."""
        res = client.get("/api/menu")
        all_items = [i for cat in res.get_json()["categories"] for i in cat["items"]]
        for item in all_items:
            assert "query" not in item
            assert "session" not in item


class TestCartEndpoint:

    def test_add_valid_item(self, client):
        res = client.post("/api/cart/add", json={"item_id": 1, "quantity": 2})
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["cart"]) == 1
        assert data["cart"][0]["quantity"] == 2

    def test_add_unavailable_item_returns_409(self, client):
        res = client.post("/api/cart/add", json={"item_id": 3, "quantity": 1})
        assert res.status_code == 409
        assert res.get_json()["code"] == "ITEM_UNAVAILABLE"

    def test_add_invalid_quantity_returns_400(self, client):
        res = client.post("/api/cart/add", json={"item_id": 1, "quantity": 25})
        assert res.status_code == 400
        assert res.get_json()["code"] == "INVALID_QUANTITY"

    def test_price_not_accepted_from_client(self, client):
        """Server must ignore any price field in request body."""
        res = client.post("/api/cart/add", json={"item_id": 1, "quantity": 1, "price": 0.01})
        assert res.status_code == 200
        cart = res.get_json()["cart"]
        assert cart[0]["price"] == 85.0  # original DB price, not 0.01


class TestCheckoutEndpoint:

    def test_checkout_empty_cart_returns_400(self, client):
        res = client.post("/api/checkout", json={"payment_token": "tok_visa", "request_id": "req-001"})
        assert res.status_code == 400
        assert res.get_json()["code"] == "EMPTY_CART"

    @patch("payment_service.stripe.Charge.create")
    def test_checkout_success_creates_order(self, mock_charge, client):
        mock_charge.return_value = {"id": "ch_test_123", "paid": True}
        # Add item to cart first
        client.post("/api/cart/add", json={"item_id": 1, "quantity": 1})
        res = client.post("/api/checkout", json={"payment_token": "tok_visa", "request_id": "req-002"})
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "Received"
        assert "order_id" in data

    @patch("payment_service.stripe.Charge.create")
    def test_idempotency_duplicate_request_returns_409(self, mock_charge, client):
        """Padlock P-06: same request_id within 60s must return 409."""
        mock_charge.return_value = {"id": "ch_idem_001", "paid": True}
        client.post("/api/cart/add", json={"item_id": 1, "quantity": 1})
        res1 = client.post("/api/checkout", json={"payment_token": "tok_visa", "request_id": "req-dupe"})
        assert res1.status_code == 201

        client.post("/api/cart/add", json={"item_id": 1, "quantity": 1})
        res2 = client.post("/api/checkout", json={"payment_token": "tok_visa", "request_id": "req-dupe"})
        assert res2.status_code == 409
        assert res2.get_json()["code"] == "DUPLICATE_REQUEST"

    @patch("payment_service.stripe.Charge.create")
    def test_payment_failure_returns_402_no_order(self, mock_charge, client):
        import stripe as stripe_lib
        mock_charge.side_effect = stripe_lib.error.APIConnectionError("timeout")
        client.post("/api/cart/add", json={"item_id": 1, "quantity": 1})
        res = client.post("/api/checkout", json={"payment_token": "tok_fail", "request_id": "req-003"})
        assert res.status_code == 402
        assert res.get_json()["code"] == "PAYMENT_FAILED"
