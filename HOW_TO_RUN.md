# How to Run the Customer Ordering System
**Salma Hani — 120210255**

---

## Prerequisites

Make sure these are installed on your machine:

| Tool | Version | Check command |
|------|---------|---------------|
| Python | 3.9 or higher | `python --version` |
| pip | any recent | `pip --version` |
| A browser | Chrome / Firefox | — |

> **Windows users:** replace `python` with `python` or `py`, and use `\` instead of `/` in paths.

---

## Step 1 — Extract and Enter the Project

```bash
# Unzip the downloaded file
unzip SalmaHani_120210255_Implementation.zip

# Enter the project folder
cd customer_ordering_system
```

---

## Step 2 — Create a Virtual Environment

Always use a virtual environment to keep dependencies isolated.

```bash
# Create it
python -m venv venv

# Activate it — Mac / Linux:
source venv/bin/activate

# Activate it — Windows:
venv\Scripts\activate
```

You should now see `(venv)` at the start of your terminal prompt.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: Flask, Flask-SQLAlchemy, Stripe, and pytest.

If pip is slow, add `-q` to suppress output:

```bash
pip install -r requirements.txt -q
```

---

## Step 4 — Set Environment Variables

Copy the example file:

```bash
# Mac / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

The `.env.example` already contains a valid Stripe **test** key — you do **not** need to create a Stripe account for the demo. The app uses SQLite by default so no database setup is needed either.

> If you want to use a real `.env` loader, install `python-dotenv` and add `load_dotenv()` to `app.py`. For the demo it is simpler to just export the variables manually (Step 4b below).

### Step 4b — Export variables (alternative to .env)

```bash
# Mac / Linux
export SECRET_KEY=demo-secret-key
export STRIPE_SECRET_KEY=sk_test_4eC39HqLyjWDarjtT1zdp7dc

# Windows Command Prompt
set SECRET_KEY=demo-secret-key
set STRIPE_SECRET_KEY=sk_test_4eC39HqLyjWDarjtT1zdp7dc
```

---

## Step 5 — Run the App

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## Step 6 — Seed the Menu (first run only)

Open a **second terminal**, activate the venv, and run:

```bash
curl -X POST http://localhost:5000/dev/seed
```

Or just open this URL in your browser:
`http://localhost:5000/dev/seed` (right-click → open as POST won't work from browser — use curl or Postman).

**Alternatively**, add this one-liner to seed from the same terminal before starting — stop the server first, run:

```python
python -c "
from app import app
from db import db
from models import MenuItem

with app.app_context():
    db.create_all()
    db.session.add_all([
        MenuItem(name='Chicken Burger', description='Crispy fried chicken with lettuce', price=85.0, category='Burgers', available=True),
        MenuItem(name='Beef Burger', description='100% beef patty with caramelized onions', price=110.0, category='Burgers', available=True),
        MenuItem(name='Grilled Salmon', description='Atlantic salmon with herbs', price=195.0, category='Mains', available=False),
        MenuItem(name='Caesar Salad', description='Romaine, croutons, parmesan', price=75.0, category='Salads', available=True),
        MenuItem(name='Margherita Pizza', description='Tomato sauce, mozzarella, fresh basil', price=120.0, category='Pizza', available=True),
        MenuItem(name='Diet Pepsi', description='330ml can', price=25.0, category='Drinks', available=True),
        MenuItem(name='Fresh Orange Juice', description='Freshly squeezed, 400ml', price=45.0, category='Drinks', available=True),
        MenuItem(name='Chocolate Lava Cake', description='Warm chocolate cake with vanilla ice cream', price=65.0, category='Desserts', available=True),
    ])
    db.session.commit()
    print('Seeded successfully.')
"
```

Then restart `python app.py`.

---

## Step 7 — Open in Browser

Go to: **http://localhost:5000**

You will see the menu with all categories.

---

## Step 8 — Demo Walk-through (for the screen recording)

Follow these steps in order for a clean ≤5 minute recording:

### 8.1 Browse the Menu
- Show the menu page loading with all categories
- Point to **Grilled Salmon** — it shows an "Out of Stock" badge and the Add button is disabled
- This demonstrates FR-08 (system rejects unavailable items) from the traceability heatmap

### 8.2 Add Items to Cart
- Click **Add +** on Chicken Burger
- Click **Add +** again on Chicken Burger → cart shows qty 2
- Click **Add +** on Diet Pepsi
- Click the cart 🛒 button in the header
- Show the cart sidebar: 2 items, total with 14% tax calculated automatically

### 8.3 Checkout
- Click **Proceed to Checkout**
- Fill in the Stripe test card:
  - Card number: `4242 4242 4242 4242`
  - Expiry: `12/27`
  - CVV: `123`
- Click **Confirm Payment**
- Show the **Order Received** confirmation with an Order ID (e.g. ORD-A3F21C)

### 8.4 Order Tracking
- The tracking page appears automatically after checkout
- Show the three-step progress tracker: **Received → Preparing → Ready**
- The status polls every 3 seconds

### 8.5 Run the Tests
Switch to your terminal and run:

```bash
pytest tests/ -v
```

You should see output like:

```
tests/test_order_service.py::TestCalculateTotal::test_basic_single_item PASSED
tests/test_order_service.py::TestCalculateTotal::test_basic_multiple_items PASSED
tests/test_order_service.py::TestCalculateTotal::test_empty_cart_raises PASSED
...
tests/test_integration.py::TestCartEndpoint::test_add_valid_item PASSED
...
========= 22 passed in 1.23s =========
```

Show the terminal on screen — this is your TDP evidence (failing tests written first, all passing now).

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
You forgot to activate the virtual environment. Run `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows) first.

### "Address already in use" on port 5000
Another process is using port 5000. Either stop it, or run Flask on a different port:
```bash
flask run --port 5001
```
Then use `http://localhost:5001`.

### "No such table: menu_items"
You skipped Step 6. Run the seed command or the Python one-liner above.

### Cart is empty after restart
Session data is stored in the browser cookie and Flask's secret key. Clearing cookies or restarting the server may clear the session. Just add items again — this is expected behaviour.

### Tests failing with "No module named 'app'"
Make sure you are running pytest **from inside the `customer_ordering_system` folder**:
```bash
cd customer_ordering_system
pytest tests/ -v
```

### Stripe payment not working
The Stripe test key in `.env.example` is a **published test key** that works without creating an account. If you see auth errors, re-export the key:
```bash
export STRIPE_SECRET_KEY=sk_test_4eC39HqLyjWDarjtT1zdp7dc
```
