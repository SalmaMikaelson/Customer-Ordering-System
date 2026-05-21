"""
models.py — Database models
Author: Salma Hani  |  ID: 120210255
"""

from db import db
from datetime import datetime
import uuid


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), default="")
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), default="Other")
    available = db.Column(db.Boolean, default=True)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: f"ORD-{uuid.uuid4().hex[:6].upper()}")
    session_id = db.Column(db.String(64), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Received")
    charge_id = db.Column(db.String(120), nullable=True)
    request_id = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(200), default="")
