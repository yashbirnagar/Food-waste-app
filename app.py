"""
AI Food Expiry & Waste Preventer
A friendly, modern web application built with Streamlit and SQLite.
Helps households track food expiration, prevent waste, and discover rule-based recipes.
"""

from datetime import date, datetime, timedelta
import io
import pandas as pd
import streamlit as st

import database as db
import recipes as rp

# ---------------------------------------------------------
# Page Configuration & Theming
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Food Expiry & Waste Preventer",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern green-themed styling
st.markdown(
    """
    <style>
    /* Global styling */
    :root {
        --primary-green: #059669;
        --light-green: #ECFDF5;
        --border-green: #A7F3D0;
    }
    
    .main-header {
        background: linear-gradient(135deg, #064E3B 0%, #059669 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .main-header p {
        color: #D1FAE5 !important;
        font-size: 1rem;
        margin: 0.4rem 0 0 0;
    }

    /* Metric cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #111827;
        margin: 0.2rem 0;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
    }

    /* Status Badges */
    .badge-pill {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        text-align: center;
        line-height: 1.2;
    }
    .badge-fresh {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #34D399;
    }
    .badge-usesoon {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FBBF24;
    }
    .badge-urgent {
        background-color: #FFEDD5;
        color: #9A3412;
        border: 1px solid #FB923C;
    }
    .badge-expired {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
    }

    /* Item Card Container */
    .food-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .food-card-urgent {
        border-left: 5px solid #EA580C;
    }
    .food-card-expired {
        border-left: 5px solid #DC2626;
    }
    .food-card-usesoon {
        border-left: 5px solid #D97706;
    }
    .food-card-fresh {
        border-left: 5px solid #059669;
    }

    /* Recipe card */
    .recipe-card {
        background: #FAFAFA;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.2rem;
        border-top: 4px solid #059669;
    }
    
    .rescue-tag {
        background-color: #FFEDD5;
        color: #C2410C;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 0.25rem;
    }
    
    .ingredient-tag-yes {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.15rem;
    }
    .ingredient-tag-no {
        background-color: #F3F4F6;
        color: #6B7280;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.15rem;
    }
    
    .rule-banner {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;
        padding: 0.85rem 1.25rem;
        font-size: 0.9rem;
        color: #166534;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Database Initialization & Auto-Seed
# ---------------------------------------------------------
db.init_db()

# Auto-seed sample data on first run if database is completely empty
db.seed_sample_data(force=False)

# ---------------------------------------------------------
# App Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>🌱 AI Food Expiry & Waste Preventer</h1>
        <p>Smart kitchen inventory management, proactive freshness tracking, and rule-based waste-prevention recipes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Controls & Quick Actions
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80",
        caption="Zero-Waste Sustainable Kitchen",
        use_container_width=True,
    )

    st.subheader("📌 Status Legend")
    st.markdown(
        """
        - 🟢 **Fresh**: 7+ days remaining
        - 🟡 **Use Soon**: 3 to 6 days remaining
        - 🟠 **Urgent**: 0 to 2 days remaining
        - 🔴 **Expired**: Past expiry date (< 0 days)
        """
    )
    st.divider()

    st.subheader("💡 Waste Prevention Tip")
    st.info(
        "**First In, First Out (FIFO):** Place newer groceries behind older items in your fridge so you reach for the urgent items first!"
    )
    
    st.divider()
    st.caption("AI Food Expiry & Waste Preventer v1.0 • Built with Streamlit & SQLite")


# ---------------------------------------------------------
# Top Navigation Tabs
# ---------------------------------------------------------
tabs = st.tabs([
    "📋 Inventory & Dashboard",
    "➕ Add Food Item",
    "🍳 Smart Recipe Suggestions",
    "📊 Waste Analytics & Reports",
    "⚙️ Settings & Sample Data",
])

# =========================================================
# TAB 1: INVENTORY & DASHBOARD
# =========================================================
with tabs[0]:
    metrics = db.get_inventory_summary_metrics()

    # KPI Statistics Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Active Items</div>
                <div class="metric-value">{metrics['total_active']}</div>
                <small style="color:#6B7280;">In Fridge / Pantry</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #059669;">
                <div class="metric-title" style="color:#059669;">🟢 Fresh</div>
                <div class="metric-value" style="color:#059669;">{metrics['fresh_count']}</div>
                <small style="color:#6B7280;">Safe for ≥ 7 days</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #D97706;">
                <div class="metric-title" style="color:#D97706;">🟡 Use Soon</div>
                <div class="metric-value" style="color:#D97706;">{metrics['use_soon_count']}</div>
                <small style="color:#6B7280;">3 - 6 days left</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #EA580C;">
                <div class="metric-title" style="color:#EA580C;">🟠 Urgent</div>
                <div class="metric-value" style="color:#EA580C;">{metrics['urgent_count']}</div>
                <small style="color:#6B7280;">≤ 2 days left!</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #DC2626;">
                <div class="metric-title" style="color:#DC2626;">🔴 Expired</div>
                <div class="metric-value" style="color:#DC2626;">{metrics['expired_count']}</div>
                <small style="color:#6B7280;">Action Needed</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #2563EB;">
                <div class="metric-title" style="color:#2563EB;">Rescue Rate</div>
                <div class="metric-value" style="color:#2563EB;">{metrics['prevention_rate']}%</div>
                <small style="color:#6B7280;">Consumed vs Wasted</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Search & Filter Controls
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1.2, 1.2, 1.2])

    with filter_col1:
        search_query = st.text_input("🔍 Search Inventory", placeholder="Search by food name (e.g. Milk, Spinach)...")

    with filter_col2:
        category_options = [
            "All", "Vegetables", "Fruits", "Dairy", "Bakery",
            "Meat & Poultry", "Pantry", "Beverages", "Leftovers", "Other"
        ]
        selected_category = st.selectbox("📂 Category", category_options)

    with filter_col3:
        status_options = ["All", "Urgent", "Use Soon", "Fresh", "Expired"]
        selected_status = st.selectbox("🏷️ Freshness Status", status_options)

    with filter_col4:
        sort_options = {
            "Expiry (Soonest First)": "expiry_date ASC",
            "Expiry (Latest First)": "expiry_date DESC",
            "Food Name (A-Z)": "name ASC",
            "Category (A-Z)": "category ASC",
        }
        selected_sort_label = st.selectbox("↕️ Sort Order", list(sort_options.keys()))
        selected_sort_val = sort_options[selected_sort_label]

    # Fetch active items
    inventory_items = db.get_active_inventory(
        category_filter=selected_category,
        status_filter=selected_status,
        search_query=search_query,
        sort_by=selected_sort_val,
    )

    st.markdown(f"#### 🥑 Current Food Inventory ({len(inventory_items)} items)")

    if not inventory_items:
        st.info("No food items match the selected filter. Try clearing filters or adding items in the 'Add Food Item' tab!")
        if st.button("🌱 Load Sample Food Items"):
            db.seed_sample_data(force=True)
            st.rerun()
    else:
        # Display as clear, interactive item rows
        for item in inventory_items:
            days = item["days_remaining"]
            status_label = item["status_label"]

            # Choose badge CSS class
            badge_class_map = {
                "Fresh": "badge-fresh",
                "Use Soon": "badge-usesoon",
                "Urgent": "badge-urgent",
                "Expired": "badge-expired",
            }
            badge_cls = badge_class_map.get(status_label, "badge-fresh")

            # Days remaining text
            if days > 1:
                days_txt = f"⏳ **{days} days** remaining"
            elif days == 1:
                days_txt = "⚠️ **Expires Tomorrow!**"
            elif days == 0:
                days_txt = "🚨 **Expires Today!**"
            else:
                days_txt = f"❌ **Expired {abs(days)} day(s) ago**"

            card_border_map = {
                "Fresh": "food-card-fresh",
                "Use Soon": "food-card-usesoon",
                "Urgent": "food-card-urgent",
                "Expired": "food-card-expired",
            }
            border_cls = card_border_map.get(status_label, "food-card-fresh")

            # Container card for each food item
            with st.container():
                st.markdown(
                    f"""
                    <div class="food-card {border_cls}">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <strong style="font-size: 1.15rem; color: #1F2937;">{item['name']}</strong>
                                <span style="margin-left: 0.5rem; color: #4B5563; font-size: 0.9rem;">
                                    ({item['quantity']} {item['unit']} • {item['category']})
                                </span>
                            </div>
                            <div>
                                <span class="badge-pill {badge_cls}">{item['status_icon']} {status_label}</span>
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.88rem; color: #4B5563; display: flex; gap: 1.5rem; flex-wrap: wrap;">
                            <span>📅 Purchased: <strong>{item['purchase_date']}</strong></span>
                            <span>⏰ Expiry: <strong>{item['expiry_date']}</strong></span>
                            <span>{days_txt}</span>
                            <span>💵 Est. Cost: <strong>${item['estimated_cost']:.2f}</strong></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Action row for this item
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.3, 1.3, 1, 1])
                
                with btn_col1:
                    with st.popover("✅ Mark Consumed", use_container_width=True):
                        st.write(f"Mark **{item['name']}** as eaten!")
                        c_note = st.text_input("Notes / Dish Made (optional):", key=f"c_note_{item['id']}", placeholder="e.g. Made soup")
                        if st.button("Confirm Consumed", key=f"btn_c_{item['id']}", type="primary"):
                            db.mark_item_consumed(item['id'], notes=c_note)
                            st.success(f"Marked {item['name']} as consumed! Great job preventing food waste!")
                            st.rerun()

                with btn_col2:
                    with st.popover("🗑️ Mark Wasted", use_container_width=True):
                        st.write(f"Mark **{item['name']}** as discarded")
                        w_reason = st.selectbox(
                            "Reason for Waste:",
                            ["Expired before use", "Spoiled / Molded", "Forgot in fridge", "Cooked too much", "Other"],
                            key=f"w_reason_{item['id']}"
                        )
                        if st.button("Confirm Wasted", key=f"btn_w_{item['id']}"):
                            db.mark_item_wasted(item['id'], notes=w_reason)
                            st.warning(f"Recorded waste for {item['name']}. We will use this in your analytics!")
                            st.rerun()

                with btn_col3:
                    with st.popover("✏️ Edit", use_container_width=True):
                        st.write(f"Edit **{item['name']}**")
                        edit_name = st.text_input("Name", value=item['name'], key=f"en_{item['id']}")
                        edit_cat = st.selectbox("Category", category_options[1:], index=category_options[1:].index(item['category']) if item['category'] in category_options[1:] else 0, key=f"ec_{item['id']}")
                        edit_qty = st.number_input("Quantity", min_value=0.1, value=float(item['quantity']), step=0.5, key=f"eq_{item['id']}")
                        edit_unit = st.text_input("Unit", value=item['unit'], key=f"eu_{item['id']}")
                        edit_exp = st.date_input("Expiry Date", value=datetime.strptime(item['expiry_date'], "%Y-%m-%d").date(), key=f"ee_{item['id']}")
                        edit_cost = st.number_input("Est. Cost ($)", min_value=0.0, value=float(item['estimated_cost']), step=0.5, key=f"ecost_{item['id']}")
                        if st.button("Save Changes", key=f"save_{item['id']}", type="primary"):
                            db.update_food_item(
                                item_id=item['id'],
                                name=edit_name,
                                category=edit_cat,
                                quantity=edit_qty,
                                unit=edit_unit,
                                purchase_date=item['purchase_date'],
                                expiry_date=edit_exp.strftime("%Y-%m-%d"),
                                estimated_cost=edit_cost,
                            )
                            st.success("Item updated!")
                            st.rerun()

                with btn_col4:
                    if st.button("❌ Delete", key=f"del_{item['id']}", use_container_width=True):
                        db.delete_food_item(item['id'])
                        st.rerun()

                st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)


# =========================================================
# TAB 2: ADD FOOD ITEM (WITH VALIDATION & QUICK BUTTONS)
# =========================================================
with tabs[1]:
    st.markdown("### ➕ Add New Food Item to Inventory")
    st.markdown("Enter your grocery or pantry items below. We will calculate the shelf life and alert you before it expires.")

    # Quick Add Perishable Shortcuts
    st.markdown("**⚡ Quick-Fill Presets for Common Perishables:**")
    quick_cols = st.columns(6)
    preset_items = [
        ("🥛 Milk", "Dairy", "Liter", 5),
        ("🍞 Bread", "Bakery", "Loaf", 5),
        ("🥚 Eggs", "Dairy", "items", 14),
        ("🥬 Spinach", "Vegetables", "g", 4),
        ("🍌 Bananas", "Fruits", "items", 4),
        ("🍗 Chicken", "Meat & Poultry", "g", 3),
    ]

    # Session state for form pre-filling
    if "form_name" not in st.session_state:
        st.session_state.form_name = ""
    if "form_cat" not in st.session_state:
        st.session_state.form_cat = "Vegetables"
    if "form_unit" not in st.session_state:
        st.session_state.form_unit = "items"
    if "form_expiry_days" not in st.session_state:
        st.session_state.form_expiry_days = 7

    for idx, (p_name, p_cat, p_unit, p_days) in enumerate(preset_items):
        with quick_cols[idx]:
            if st.button(p_name, use_container_width=True, key=f"preset_{idx}"):
                st.session_state.form_name = p_name.split(" ", 1)[-1]
                st.session_state.form_cat = p_cat
                st.session_state.form_unit = p_unit
                st.session_state.form_expiry_days = p_days
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("add_food_form", clear_on_submit=False):
        form_col1, form_col2 = st.columns(2)

        with form_col1:
            food_name = st.text_input(
                "Food Name *",
                value=st.session_state.form_name,
                placeholder="e.g. Fresh Tomatoes, Sliced Cheddar, Greek Yogurt",
                help="Name of the food item or produce.",
            )

            category = st.selectbox(
                "Category *",
                [
                    "Vegetables", "Fruits", "Dairy", "Meat & Poultry", "Bakery",
                    "Pantry", "Beverages", "Leftovers", "Snacks", "Other"
                ],
                index=[
                    "Vegetables", "Fruits", "Dairy", "Meat & Poultry", "Bakery",
                    "Pantry", "Beverages", "Leftovers", "Snacks", "Other"
                ].index(st.session_state.form_cat)
                if st.session_state.form_cat in [
                    "Vegetables", "Fruits", "Dairy", "Meat & Poultry", "Bakery",
                    "Pantry", "Beverages", "Leftovers", "Snacks", "Other"
                ] else 0,
            )

            qty_col, unit_col = st.columns(2)
            with qty_col:
                quantity = st.number_input("Quantity *", min_value=0.1, max_value=9999.0, value=1.0, step=0.5)
            with unit_col:
                unit = st.selectbox(
                    "Unit *",
                    ["items", "kg", "g", "Liter", "ml", "Loaf", "Pack", "Jar", "Can", "Bunch", "Portion"],
                    index=["items", "kg", "g", "Liter", "ml", "Loaf", "Pack", "Jar", "Can", "Bunch", "Portion"].index(st.session_state.form_unit)
                    if st.session_state.form_unit in ["items", "kg", "g", "Liter", "ml", "Loaf", "Pack", "Jar", "Can", "Bunch", "Portion"] else 0,
                )

        with form_col2:
            today_date = date.today()
            purchase_date = st.date_input("Purchase Date *", value=today_date, max_value=today_date + timedelta(days=365))

            # Expiry date computation
            default_exp = today_date + timedelta(days=st.session_state.form_expiry_days)
            expiry_date = st.date_input("Expiry Date *", value=default_exp)

            estimated_cost = st.number_input(
                "Estimated Cost ($) [Optional]",
                min_value=0.0,
                max_value=9999.0,
                value=0.0,
                step=0.5,
                help="Helps track financial savings when consumed vs lost when wasted.",
            )

        # Quick expiry adjustment helpers
        st.markdown("**Quick Expiry Date Shortcuts:**")
        exp_shortcut_cols = st.columns(5)
        with exp_shortcut_cols[0]:
            if st.form_submit_button("📅 +2 Days"):
                st.session_state.form_expiry_days = 2
                st.rerun()
        with exp_shortcut_cols[1]:
            if st.form_submit_button("📅 +5 Days"):
                st.session_state.form_expiry_days = 5
                st.rerun()
        with exp_shortcut_cols[2]:
            if st.form_submit_button("📅 +1 Week"):
                st.session_state.form_expiry_days = 7
                st.rerun()
        with exp_shortcut_cols[3]:
            if st.form_submit_button("📅 +2 Weeks"):
                st.session_state.form_expiry_days = 14
                st.rerun()
        with exp_shortcut_cols[4]:
            if st.form_submit_button("📅 +1 Month"):
                st.session_state.form_expiry_days = 30
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✅ Add Item to Inventory", type="primary", use_container_width=True)

    # Input Validation & Insertion Logic
    if submit_btn:
        has_errors = False

        if not food_name or not food_name.strip():
            st.error("❌ Validation Error: Food Item Name cannot be empty.")
            has_errors = True

        if quantity <= 0:
            st.error("❌ Validation Error: Quantity must be greater than zero.")
            has_errors = True

        if expiry_date < purchase_date:
            st.warning("⚠️ Warning: Expiry date is set before the purchase date. Please double check your dates.")

        if not has_errors:
            # Add to SQLite database
            db.add_food_item(
                name=food_name.strip(),
                category=category,
                quantity=quantity,
                unit=unit,
                purchase_date=purchase_date.strftime("%Y-%m-%d"),
                expiry_date=expiry_date.strftime("%Y-%m-%d"),
                estimated_cost=estimated_cost,
            )

            days_left = (expiry_date - date.today()).days
            status_label, _, icon = db.get_status_info(days_left)

            st.success(
                f"🎉 Added **{food_name.strip().title()}** ({quantity} {unit}) to your inventory! "
                f"Status: {icon} **{status_label}** ({days_left} days left until expiry)."
            )

            # Reset session state form name
            st.session_state.form_name = ""
            st.session_state.form_expiry_days = 7


# =========================================================
# TAB 3: RULE-BASED RECIPE SUGGESTIONS
# =========================================================
with tabs[2]:
    st.markdown("### 🍳 Rule-Based Recipe Suggestions")
    
    # Transparent Rule-Based System Explanation Banner
    st.markdown(
        """
        <div class="rule-banner">
            <strong>🧠 How the Rule-Based AI Engine Works:</strong><br>
            This system uses a transparent <em>Rule-Based Heuristic Matching Algorithm</em> (not an unpredictable black-box ML model). 
            It compares your currently active ingredients against a culinary knowledge base of zero-waste recipes, 
            identifies missing vs. available components, and <strong>prioritizes recipes that use your Urgent (≤ 2 days) and Use Soon (3-6 days)</strong> ingredients to prevent food spoilage!
        </div>
        """,
        unsafe_allow_html=True,
    )

    recipe_filter_col1, recipe_filter_col2 = st.columns([1.5, 1])
    with recipe_filter_col1:
        prioritize_urgent = st.checkbox("🚨 Prioritize Rescuing Urgent & Expiring Items First", value=True)
    with recipe_filter_col2:
        only_cookable = st.checkbox("✨ Only Show Ready-to-Cook (All Required Ingredients Available)", value=False)

    active_items = db.get_active_inventory()
    urgent_items_list = [item["name"] for item in active_items if item["status_label"] == "Urgent"]
    use_soon_items_list = [item["name"] for item in active_items if item["status_label"] == "Use Soon"]

    if urgent_items_list:
        st.warning(f"🚨 **High-Priority Items Expiring Soon:** {', '.join(urgent_items_list)}. Cook recipes below to rescue them!")

    suggestions = rp.get_rule_based_recipe_suggestions(
        active_items=active_items,
        prioritize_urgent=prioritize_urgent,
    )

    if only_cookable:
        suggestions = [s for s in suggestions if s["can_cook_now"]]

    if not suggestions:
        st.info("No recipes matched your available ingredients. Try adding basic items like Eggs, Bread, Milk, Spinach, Rice, or Potatoes to unlock suggestions!")
    else:
        st.markdown(f"Found **{len(suggestions)}** recipe suggestions based on your active inventory:")

        for rec in suggestions:
            rescues = rec["rescued_urgent"] + rec["rescued_use_soon"]

            # Format tags for display
            matched_html = "".join([f'<span class="ingredient-tag-yes">✅ {item}</span>' for item in rec["matched_required"] + rec["matched_optional"]])
            missing_html = "".join([f'<span class="ingredient-tag-no">🛒 Need: {item}</span>' for item in rec["missing_required"] + rec["missing_optional"]])

            urgent_rescue_html = ""
            if rec["rescued_urgent"]:
                urgent_rescue_html = f'<div class="rescue-tag">🚨 Rescues Urgent: {", ".join(rec["rescued_urgent"])}</div>'
            elif rec["rescued_use_soon"]:
                urgent_rescue_html = f'<div class="rescue-tag" style="background-color:#FEF3C7; color:#92400E;">🟡 Uses: {", ".join(rec["rescued_use_soon"])}</div>'

            with st.container():
                st.markdown(
                    f"""
                    <div class="recipe-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                            <div>
                                <h3 style="margin: 0; color: #065F46;">{rec['title']}</h3>
                                <p style="margin: 0.2rem 0; color: #4B5563; font-size: 0.88rem;">
                                    📂 {rec['category']} • ⏱️ {rec['time']} • 📊 Difficulty: {rec['difficulty']}
                                </p>
                                {urgent_rescue_html}
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.1rem; font-weight: 800; color: {'#059669' if rec['match_score'] >= 75 else '#D97706'};">
                                    {rec['match_score']}% Match
                                </span><br>
                                <small style="color: #6B7280;">{'✨ Ready to cook!' if rec['can_cook_now'] else 'Needs a few items'}</small>
                            </div>
                        </div>
                        <div style="margin-top: 0.75rem;">
                            <strong>Your Ingredients:</strong> {matched_html if matched_html else '<span style=\"color:#9CA3AF;\">None</span>'}<br>
                            <strong>Missing / Optional:</strong> {missing_html if missing_html else '<span style=\"color:#059669;\">None! You have everything!</span>'}
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.86rem; color: #047857;">
                            💡 <em>Waste Tip: {rec['waste_tip']}</em>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Expandable recipe cooking steps
                with st.expander(f"📖 View Cooking Instructions for {rec['title']}"):
                    st.markdown("**Step-by-Step Instructions:**")
                    for s_idx, step in enumerate(rec["instructions"], 1):
                        st.markdown(f"**Step {s_idx}:** {step}")

                    # Helper action to mark ingredients consumed
                    if rec["matched_required"]:
                        st.markdown("---")
                        st.write("🍳 Cooked this dish? Mark your used inventory items as consumed:")
                        if st.button(f"Mark Used Ingredients for '{rec['title']}' as Consumed", key=f"cook_{rec['id']}"):
                            # Find matching inventory items and mark them
                            matched_lower = [m.lower() for m in rec["matched_required"]]
                            marked_count = 0
                            for itm in active_items:
                                for m in matched_lower:
                                    if m in itm["name"].lower():
                                        db.mark_item_consumed(itm["id"], notes=f"Cooked in {rec['title']}")
                                        marked_count += 1
                                        break
                            st.success(f"Marked {marked_count} ingredient(s) as consumed! Awesome zero-waste cooking!")
                            st.rerun()


# =========================================================
# TAB 4: WASTE ANALYTICS & REPORTS
# =========================================================
with tabs[3]:
    st.markdown("### 📊 Household Food Waste Report & Analytics")
    st.markdown("Monitor your consumption habits, identify items that spoil most frequently, and measure your environmental impact.")

    metrics = db.get_inventory_summary_metrics()
    history_items = db.get_all_history_items()

    # KPI Banner
    rep_col1, rep_col2, rep_col3, rep_col4 = st.columns(4)
    with rep_col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #059669;">
                <div class="metric-title" style="color: #059669;">Food Rescue Efficiency</div>
                <div class="metric-value" style="color: #059669;">{metrics['prevention_rate']}%</div>
                <small style="color:#6B7280;">Goal: > 80%</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rep_col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #2563EB;">
                <div class="metric-title" style="color: #2563EB;">Items Consumed</div>
                <div class="metric-value" style="color: #2563EB;">{metrics['consumed_count']}</div>
                <small style="color:#6B7280;">Successfully Eaten</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rep_col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #DC2626;">
                <div class="metric-title" style="color: #DC2626;">Items Wasted</div>
                <div class="metric-value" style="color: #DC2626;">{metrics['wasted_count']}</div>
                <small style="color:#6B7280;">Lost to Spoilage</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rep_col4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #10B981;">
                <div class="metric-title" style="color: #10B981;">Cost Value Saved</div>
                <div class="metric-value" style="color: #10B981;">${metrics['cost_saved']:.2f}</div>
                <small style="color:#DC2626;">Lost: ${metrics['cost_lost']:.2f}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 🥧 Outcome Distribution (Consumed vs Wasted)")
        outcome_df = pd.DataFrame({
            "Outcome": ["Consumed (Rescued)", "Wasted (Discarded)"],
            "Count": [metrics["consumed_count"], metrics["wasted_count"]],
        })
        if metrics["consumed_count"] + metrics["wasted_count"] > 0:
            st.bar_chart(outcome_df.set_index("Outcome"), color="#059669")
        else:
            st.info("No consumption or waste history yet. Mark items as consumed or wasted in the inventory tab to generate charts!")

    with chart_col2:
        st.markdown("#### 📂 Waste Breakdown by Food Category")
        wasted_records = [item for item in history_items if item["status"] == "wasted"]
        if wasted_records:
            w_cat_counts = {}
            for w in wasted_records:
                cat = w["category"]
                w_cat_counts[cat] = w_cat_counts.get(cat, 0) + 1
            w_cat_df = pd.DataFrame(list(w_cat_counts.items()), columns=["Category", "Wasted Items"]).sort_values("Wasted Items", ascending=False)
            st.bar_chart(w_cat_df.set_index("Category"), color="#DC2626")
        else:
            st.info("No items have been wasted yet! Keep up the great work.")

    # Tailored Zero-Waste Insights
    st.markdown("---")
    st.markdown("#### 🌿 Personalized Food Waste Insights")
    insight_cols = st.columns(3)
    with insight_cols[0]:
        st.success(
            "**🥬 Greens & Herbs:** Wrap fresh herbs in a damp paper towel and store in an airtight container to extend life by up to 10 days."
        )
    with insight_cols[1]:
        st.warning(
            "**🧀 Dairy & Cheeses:** Shred and freeze cheese blocks that are nearing their expiration date. They melt just like fresh cheese!"
        )
    with insight_cols[2]:
        st.info(
            "**🍞 Stale Bakery:** Bread can be sliced and frozen immediately. Defrost individual slices directly in the toaster for a fresh crunch."
        )

    # Detailed History Table
    st.markdown("---")
    st.markdown("#### 📜 Food Action History Log")
    if history_items:
        hist_display = []
        for h in history_items:
            hist_display.append({
                "ID": h["id"],
                "Food Name": h["name"],
                "Category": h["category"],
                "Quantity": f"{h['quantity']} {h['unit']}",
                "Status": "✅ Consumed" if h["status"] == "consumed" else "🗑️ Wasted",
                "Action Date": h["action_date"],
                "Notes / Reason": h["action_notes"] or "-",
                "Est. Value ($)": f"${h['estimated_cost']:.2f}",
            })
        st.dataframe(pd.DataFrame(hist_display), use_container_width=True)
    else:
        st.caption("No historical records yet.")


# =========================================================
# TAB 5: SETTINGS & SAMPLE DATA
# =========================================================
with tabs[4]:
    st.markdown("### ⚙️ Settings, Data Management & Backup")
    st.markdown("Manage your local SQLite storage, export inventory records, or reload demonstration data.")

    set_col1, set_col2 = st.columns(2)

    with set_col1:
        st.markdown("#### 📦 Sample Data Management")
        st.write("Want to test the app with a realistic set of fresh, expiring, urgent, and expired items?")
        if st.button("🌱 Load Complete Starter Sample Data", type="primary", use_container_width=True):
            db.seed_sample_data(force=True)
            st.success("Sample data successfully loaded into SQLite database! Switch to the Inventory or Recipes tab to explore.")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📥 Export Active Inventory")
        active_items = db.get_active_inventory()
        if active_items:
            df_export = pd.DataFrame(active_items)
            # Remove internal styling columns for export
            export_cols = [c for c in df_export.columns if not c.startswith("status_")]
            csv_buffer = io.StringIO()
            df_export[export_cols].to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Download Active Inventory as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"food_inventory_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No active inventory to export.")

    with set_col2:
        st.markdown("#### 🗑️ Clear Database Records")
        st.write("Permanently delete all food items and historical records from SQLite.")
        with st.popover("⚠️ Wipe All Data", use_container_width=True):
            st.write("Are you sure? This will permanently remove all active items, consumption history, and waste analytics.")
            if st.button("Confirm: Delete Everything", key="confirm_wipe", type="secondary"):
                db.clear_database()
                st.warning("Database cleared.")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ℹ️ System Architecture & Transparency")
        st.markdown(
            """
            - **Storage Engine**: Local SQLite (`food_waste.db`).
            - **Algorithm**: Deterministic rule-based priority heuristics (no external AI calls, no data leaves your machine).
            - **Status Classification Criteria**:
              - `Fresh`: $\\ge 7$ days until expiry
              - `Use Soon`: $3 - 6$ days until expiry
              - `Urgent`: $0 - 2$ days until expiry
              - `Expired`: $< 0$ days past expiry
            """
        )
