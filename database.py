"""
database.py - SQLite Database Management for AI Food Expiry & Waste Preventer
Handles table creation, inventory management, status tracking, and waste analytics.
"""

import sqlite3
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

DB_NAME = "food_waste.db"


def get_connection():
    """Returns a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if it doesn't already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active', -- 'active', 'consumed', 'wasted'
                action_date TEXT,                      -- date when marked consumed or wasted
                action_notes TEXT,                     -- notes or reason for waste/consumption
                estimated_cost REAL DEFAULT 0.0,       -- estimated cost for savings/waste tracking
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def calculate_days_remaining(expiry_date_str: str) -> int:
    """Calculates integer days remaining until expiry compared to current date."""
    try:
        expiry = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        today = date.today()
        return (expiry - today).days
    except (ValueError, TypeError):
        return 0


def get_status_info(days_remaining: int) -> Tuple[str, str, str]:
    """
    Returns (status_label, badge_color_code, badge_icon) based on days remaining:
      - Expired: < 0 days (Red)
      - Urgent: 0 to 2 days (Orange/Red)
      - Use Soon: 3 to 6 days (Amber/Yellow)
      - Fresh: >= 7 days (Emerald Green)
    """
    if days_remaining < 0:
        return "Expired", "#DC2626", "🔴"
    elif 0 <= days_remaining <= 2:
        return "Urgent", "#EA580C", "🟠"
    elif 3 <= days_remaining <= 6:
        return "Use Soon", "#D97706", "🟡"
    else:
        return "Fresh", "#059669", "🟢"


def add_food_item(
    name: str,
    category: str,
    quantity: float,
    unit: str,
    purchase_date: str,
    expiry_date: str,
    estimated_cost: float = 0.0,
) -> int:
    """Inserts a new active food item into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO food_items (
                name, category, quantity, unit, purchase_date, expiry_date,
                status, estimated_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
            """,
            (
                name.strip().title(),
                category.strip(),
                float(quantity),
                unit.strip(),
                purchase_date,
                expiry_date,
                float(estimated_cost or 0.0),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def update_food_item(
    item_id: int,
    name: str,
    category: str,
    quantity: float,
    unit: str,
    purchase_date: str,
    expiry_date: str,
    estimated_cost: float = 0.0,
):
    """Updates an existing food item."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE food_items
            SET name = ?, category = ?, quantity = ?, unit = ?,
                purchase_date = ?, expiry_date = ?, estimated_cost = ?
            WHERE id = ?
            """,
            (
                name.strip().title(),
                category.strip(),
                float(quantity),
                unit.strip(),
                purchase_date,
                expiry_date,
                float(estimated_cost or 0.0),
                item_id,
            ),
        )
        conn.commit()


def mark_item_consumed(item_id: int, notes: str = ""):
    """Marks an item as consumed and records today's date."""
    today_str = date.today().strftime("%Y-%m-%d")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE food_items
            SET status = 'consumed', action_date = ?, action_notes = ?
            WHERE id = ?
            """,
            (today_str, notes.strip(), item_id),
        )
        conn.commit()


def mark_item_wasted(item_id: int, notes: str = ""):
    """Marks an item as wasted and records today's date."""
    today_str = date.today().strftime("%Y-%m-%d")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE food_items
            SET status = 'wasted', action_date = ?, action_notes = ?
            WHERE id = ?
            """,
            (today_str, notes.strip(), item_id),
        )
        conn.commit()


def delete_food_item(item_id: int):
    """Permanently deletes a food item record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
        conn.commit()


def get_active_inventory(
    category_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    sort_by: str = "expiry_date ASC",
) -> List[Dict]:
    """
    Fetches active inventory items, enriched with days_remaining and freshness status.
    Supports filtering by category, status, and search query.
    """
    valid_sorts = {
        "expiry_date ASC": "expiry_date ASC",
        "expiry_date DESC": "expiry_date DESC",
        "name ASC": "name ASC",
        "category ASC": "category ASC",
    }
    order_clause = valid_sorts.get(sort_by, "expiry_date ASC")

    query = "SELECT * FROM food_items WHERE status = 'active'"
    params = []

    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    if search_query and search_query.strip():
        query += " AND name LIKE ?"
        params.append(f"%{search_query.strip()}%")

    query += f" ORDER BY {order_clause}"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    items = []
    for row in rows:
        item = dict(row)
        days = calculate_days_remaining(item["expiry_date"])
        status_label, color, icon = get_status_info(days)
        item["days_remaining"] = days
        item["status_label"] = status_label
        item["status_color"] = color
        item["status_icon"] = icon

        # Filter by computed status if requested
        if status_filter and status_filter != "All":
            if item["status_label"] != status_filter:
                continue

        items.append(item)

    return items


def get_inventory_summary_metrics() -> Dict:
    """Calculates live KPI metrics for active inventory and waste prevention."""
    active_items = get_active_inventory()
    
    total_active = len(active_items)
    fresh_count = sum(1 for item in active_items if item["status_label"] == "Fresh")
    use_soon_count = sum(1 for item in active_items if item["status_label"] == "Use Soon")
    urgent_count = sum(1 for item in active_items if item["status_label"] == "Urgent")
    expired_count = sum(1 for item in active_items if item["status_label"] == "Expired")

    # Historical stats
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*), SUM(estimated_cost) FROM food_items GROUP BY status")
        status_rows = cursor.fetchall()

    history_counts = {"active": 0, "consumed": 0, "wasted": 0}
    history_costs = {"active": 0.0, "consumed": 0.0, "wasted": 0.0}

    for row in status_rows:
        s = row[0]
        c = row[1] or 0
        cost = row[2] or 0.0
        if s in history_counts:
            history_counts[s] = c
            history_costs[s] = cost

    total_resolved = history_counts["consumed"] + history_counts["wasted"]
    if total_resolved > 0:
        prevention_rate = round((history_counts["consumed"] / total_resolved) * 100, 1)
    else:
        prevention_rate = 100.0 if history_counts["consumed"] > 0 else 0.0

    return {
        "total_active": total_active,
        "fresh_count": fresh_count,
        "use_soon_count": use_soon_count,
        "urgent_count": urgent_count,
        "expired_count": expired_count,
        "consumed_count": history_counts["consumed"],
        "wasted_count": history_counts["wasted"],
        "prevention_rate": prevention_rate,
        "cost_saved": history_costs["consumed"],
        "cost_lost": history_costs["wasted"],
    }


def get_all_history_items() -> List[Dict]:
    """Retrieves all consumed and wasted food items for analytics and history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM food_items 
            WHERE status IN ('consumed', 'wasted')
            ORDER BY action_date DESC, id DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def seed_sample_data(force: bool = False):
    """
    Populates sample data if database is empty or if forced by the user.
    Includes items in Fresh, Use Soon, Urgent, and Expired states,
    as well as historical consumed/wasted items for analytics.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM food_items")
        count = cursor.fetchone()[0]

    if count > 0 and not force:
        return False

    if force:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_items")
            conn.commit()

    today = date.today()

    sample_items = [
        # Urgent items (0-2 days remaining)
        ("Whole Milk", "Dairy", 1.0, "Liter", (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), "active", None, "", 3.50),
        ("Ripe Avocados", "Fruits", 3.0, "items", (today - timedelta(days=4)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), "active", None, "", 4.20),
        ("Fresh Spinach", "Vegetables", 250.0, "g", (today - timedelta(days=6)).strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), "active", None, "", 2.80),
        
        # Use Soon items (3-6 days remaining)
        ("Greek Yogurt", "Dairy", 500.0, "g", (today - timedelta(days=8)).strftime("%Y-%m-%d"), (today + timedelta(days=4)).strftime("%Y-%m-%d"), "active", None, "", 4.50),
        ("Whole Wheat Bread", "Bakery", 1.0, "Loaf", (today - timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "active", None, "", 2.99),
        ("Chicken Breast", "Meat & Poultry", 500.0, "g", (today - timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), "active", None, "", 7.50),
        ("Strawberries", "Fruits", 1.0, "Pack", (today - timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=4)).strftime("%Y-%m-%d"), "active", None, "", 3.99),

        # Fresh items (7+ days remaining)
        ("Brown Eggs", "Dairy", 12.0, "items", (today - timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=14)).strftime("%Y-%m-%d"), "active", None, "", 4.00),
        ("Cheddar Cheese", "Dairy", 200.0, "g", (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=18)).strftime("%Y-%m-%d"), "active", None, "", 5.20),
        ("Carrots", "Vegetables", 1.0, "kg", (today - timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=12)).strftime("%Y-%m-%d"), "active", None, "", 1.80),
        ("Potatoes", "Vegetables", 2.0, "kg", (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=21)).strftime("%Y-%m-%d"), "active", None, "", 3.00),
        ("Cooked Basmati Rice", "Pantry", 500.0, "g", (today - timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=8)).strftime("%Y-%m-%d"), "active", None, "", 1.50),
        ("Apples", "Fruits", 6.0, "items", (today - timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=10)).strftime("%Y-%m-%d"), "active", None, "", 3.50),

        # Expired active item (< 0 days remaining)
        ("Sliced Ham", "Meat & Poultry", 150.0, "g", (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today - timedelta(days=1)).strftime("%Y-%m-%d"), "active", None, "", 3.80),

        # Historical Consumed items
        ("Bananas", "Fruits", 4.0, "items", (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today - timedelta(days=4)).strftime("%Y-%m-%d"), "consumed", (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Used in morning smoothie", 2.20),
        ("Cottage Cheese", "Dairy", 250.0, "g", (today - timedelta(days=12)).strftime("%Y-%m-%d"), (today - timedelta(days=5)).strftime("%Y-%m-%d"), "consumed", (today - timedelta(days=6)).strftime("%Y-%m-%d"), "Eaten with fruit bowl", 3.10),
        ("Pasta Sauce", "Pantry", 1.0, "Jar", (today - timedelta(days=15)).strftime("%Y-%m-%d"), (today - timedelta(days=2)).strftime("%Y-%m-%d"), "consumed", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Dinner pasta night", 2.75),
        ("Broccoli", "Vegetables", 300.0, "g", (today - timedelta(days=9)).strftime("%Y-%m-%d"), (today - timedelta(days=3)).strftime("%Y-%m-%d"), "consumed", (today - timedelta(days=4)).strftime("%Y-%m-%d"), "Steamed with garlic", 2.50),

        # Historical Wasted items
        ("Sour Cream", "Dairy", 1.0, "Tub", (today - timedelta(days=20)).strftime("%Y-%m-%d"), (today - timedelta(days=8)).strftime("%Y-%m-%d"), "wasted", (today - timedelta(days=7)).strftime("%Y-%m-%d"), "Molded before opening", 2.40),
        ("Baguette", "Bakery", 1.0, "item", (today - timedelta(days=14)).strftime("%Y-%m-%d"), (today - timedelta(days=9)).strftime("%Y-%m-%d"), "wasted", (today - timedelta(days=9)).strftime("%Y-%m-%d"), "Turned completely rock hard", 2.10),
        ("Salad Mix", "Vegetables", 1.0, "Bag", (today - timedelta(days=16)).strftime("%Y-%m-%d"), (today - timedelta(days=11)).strftime("%Y-%m-%d"), "wasted", (today - timedelta(days=10)).strftime("%Y-%m-%d"), "Turned slimy in the crisper drawer", 3.25),
    ]

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO food_items (
                name, category, quantity, unit, purchase_date, expiry_date,
                status, action_date, action_notes, estimated_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample_items,
        )
        conn.commit()

    return True


def clear_database():
    """Wipes all records from the food_items table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_items")
        conn.commit()
