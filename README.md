# Customer-Ordering-System
A system that automates the ordering process for a restaurant using a web-based workflow.
[README.md](https://github.com/user-attachments/files/28093739/README.md)
# Customer Ordering System
**Salma Hani — ID: 120210255**

## Setup & Run

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set environment variables (or leave defaults for dev)
export SECRET_KEY=your-secret-key
export STRIPE_SECRET_KEY=sk_test_...
export DATABASE_URL=sqlite:///orders.db   # or postgresql://...

# 3. Run the app
python app.py

# 4. Seed the menu (first run only)
curl -X POST http://localhost:5000/dev/seed

# 5. Open in browser
http://localhost:5000
```

## Run Tests

```bash
# Unit + integration tests
pytest tests/ -v

# E2E Playwright tests
npx playwright install
npx playwright test tests/e2e/specs/
```

## Project Structure

```
customer_ordering_system/
├── app.py               # Flask routes — entry point
├── db.py                # SQLAlchemy instance
├── models.py            # DB models: MenuItem, Order, OrderItem
├── order_service.py     # calculate_total(), create_order(), idempotency
├── cart_service.py      # add_to_cart(), validate_cart_items()
├── payment_service.py   # Stripe charge with timeout wrapper
├── auth_service.py      # Session binding decorator
├── requirements.txt
├── static/
│   └── style.css        # Frontend styles
├── templates/
│   └── order.html       # Single-page frontend
└── tests/
    ├── test_order_service.py   # Unit tests (TDP — written before implementation)
    ├── test_integration.py     # Integration tests (Flask test client)
    └── e2e/
        ├── pages/              # Page Object Model
        │   ├── MenuPage.js
        │   ├── CartPage.js
        │   ├── CheckoutPage.js
        │   └── TrackingPage.js
        └── specs/              # Playwright E2E tests
            ├── checkout.spec.js
            └── browse_and_track.spec.js
```
