# 🌱 AI Food Expiry & Waste Preventer

A friendly, modern, and zero-cost Python web application built with **Streamlit** and **SQLite** to help households track food expiration dates, reduce spoilage, make smart use of ingredients, and prevent unnecessary food waste.

---

## ✨ Features

1. **Add Food Items with Rich Attributes**:
   - Record food name, category (Vegetables, Fruits, Dairy, Bakery, Meat, etc.), quantity, unit, purchase date, expiry date, and optional estimated cost.
   - Quick perishable presets (Milk, Bread, Eggs, Spinach, Bananas, Chicken) for one-click entry.
   - Quick date offset shortcuts (`+2 Days`, `+5 Days`, `+1 Week`, `+2 Weeks`, `+1 Month`).
2. **Automatic Expiry & Shelf-Life Calculation**:
   - Calculates the exact number of days remaining until expiration relative to the current date.
   - Distinguishes "Expires Today!", "Expires Tomorrow!", remaining days, or days past expiry.
3. **Smart Status Classification Labels**:
   - 🟢 **Fresh**: 7 or more days remaining.
   - 🟡 **Use Soon**: 3 to 6 days remaining.
   - 🟠 **Urgent**: 0 to 2 days remaining (requires immediate rescue).
   - 🔴 **Expired**: Past expiration date.
4. **Live Inventory & Dashboard Statistics**:
   - Top KPI cards displaying Total Active Items, Fresh, Use Soon, Urgent, Expired, and Waste Prevention Rate (%).
   - Search by name, filter by category, filter by freshness status, and sort by expiry date.
5. **Rule-Based Recipe Suggestions**:
   - A deterministic, rule-based heuristic matching engine that evaluates your active ingredients against a zero-waste recipe database.
   - **Urgency Prioritization**: Boosts recipes that utilize ingredients flagged as *Urgent* or *Use Soon* to rescue them before they spoil.
   - Transparently indicates which ingredients you have on hand and which are missing.
   - *Note: This uses deterministic rule-based algorithms, not an external or trained machine learning black box.*
6. **Mark Food as Consumed or Wasted**:
   - Mark consumed items to track successful food rescue and log dish notes.
   - Mark wasted items and record reasons (e.g., "Spoiled/molded", "Forgotten in fridge") for waste analysis.
   - Edit item attributes or delete entries anytime.
7. **Comprehensive Food Waste Report & Visual Analytics**:
   - Visual charts tracking Consumed vs. Wasted outcomes.
   - Category breakdown identifying which food categories spoil most frequently.
   - Tracks estimated financial value saved vs. lost.
   - Personalized zero-waste tips based on spoilage trends.
8. **Permanent Local Storage via SQLite**:
   - All items, status changes, and history are stored locally in `food_waste.db`.
   - No external database setup or cloud account required.
9. **Modern, Clean, Green-Themed Responsive UI**:
   - Curated emerald and forest-green color palette with card containers, badges, and clean typography.
10. **Sample Data & Robust Input Validation**:
    - Pre-seeded sample data on first launch so you can test features immediately.
    - One-click "Load Sample Data" and "Reset Database" options.
    - Input validation checks for non-empty names, positive quantities, and date consistency warnings.
    - Export active inventory to CSV.

---

## 🏗️ Project Architecture

```
AI food waste/
├── app.py              # Main Streamlit web application & user interface
├── database.py         # SQLite database schema, CRUD operations, & metrics
├── recipes.py          # Rule-based recipe engine & zero-waste culinary knowledge base
├── requirements.txt    # Project dependencies (streamlit, pandas)
└── README.md           # Documentation and setup guide
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.9+** (Tested on Python 3.10, 3.11, 3.12, 3.13)
- `pip` (Python package installer)

### 2. Clone or Navigate to the Project Folder
Open your terminal or command prompt:
```bash
cd "AI food waste"
```

### 3. (Optional but Recommended) Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install Streamlit and Pandas using the included `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Launch the Application
Run the Streamlit application:
```bash
streamlit run app.py
```

The app will automatically open in your default browser at:
```
http://localhost:8501
```

---

## 📖 How It Works

### Freshness Status Calculation
The application calculates days remaining using:
$$\text{Days Remaining} = \text{Expiry Date} - \text{Current Date}$$

| Status | Days Remaining | Action Recommended |
|---|---|---|
| 🟢 **Fresh** | $\ge 7\text{ days}$ | Safe for standard storage |
| 🟡 **Use Soon** | $3 \text{ to } 6\text{ days}$ | Plan meals around these items this week |
| 🟠 **Urgent** | $0 \text{ to } 2\text{ days}$ | Cook immediately using suggested recipes |
| 🔴 **Expired** | $< 0\text{ days}$ | Inspect for safety and discard or compost if spoiled |

### Rule-Based Recipe Engine
The recipe suggestions use a transparent heuristic algorithm:
1. **Inventory Matching**: Tokenizes active inventory items (e.g., "Whole Milk" matches "milk").
2. **Match Score**: Evaluates coverage of required core ingredients (75% weight) and optional ingredients (25% weight).
3. **Rescue Weighting**: Recipes that utilize ingredients with `Urgent` or `Use Soon` status receive priority placement at the top of recommendations.
4. **Transparency**: The matching logic is deterministic and explainable without third-party AI APIs or costs.

---

## 🔒 Privacy & Local Execution
- **100% Offline & Local**: Your pantry data and eating habits remain on your computer in `food_waste.db`.
- **Zero Paid APIs**: No OpenAI, Anthropic, or external cloud services needed.

---

## 📄 License
This project is open-source and free to use for personal or educational purposes.
