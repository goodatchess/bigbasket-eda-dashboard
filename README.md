# BigBasket FMCG — EDA & Supply Chain Analytics Dashboard

Exploratory data analysis and interactive Streamlit dashboard for BigBasket's grocery catalogue — 27,555 SKUs across 11 categories and 90 sub-categories. Includes a supply chain intelligence layer with simulated inventory metrics relevant to FMCG operations.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Pandas](https://img.shields.io/badge/Pandas-2.0-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-orange)

---

## What's inside

| File | What it does |
|------|-------------|
| `bigbasket_eda_extended.ipynb` | Full EDA notebook — cleaning, KPIs, 11 charts, SC metrics, insights |
| `app.py` | Streamlit dashboard — 6 tabs, 15 charts, sidebar filters |
| `requirements.txt` | Python dependencies |

---

## Dashboard Tabs

| Tab | Charts |
|-----|--------|
| 📦 Overview | SKU by category, price tier donut, price histogram, sub-category counts |
| 💰 Pricing & Discounts | Discount by category, MRP vs sale price, discount histogram, heatmap |
| ⭐ Ratings | Rating by category, violin plot, discount vs rating scatter, value score |
| 🏷️ Brands | Top brands by SKU, top brands by discount, brand deep-dive selector |
| 🔵 Bubble Chart | SKU count vs rating bubble chart + key insights |
| 🏭 Supply Chain | Days of supply, inventory turnover, stock vs reorder point, stockout risk map |

---

## Supply Chain Module

The SC tab simulates inventory parameters at category level using catalogue signals as demand proxies — relevant to FMCG operations roles.

**Metrics calculated:**

| Metric | Formula |
|--------|---------|
| Demand Velocity Score | `(SKU Count / Max) × 0.6 + (Avg Discount / Max) × 0.4` |
| Safety Stock | `Z × σ(demand) × √(Lead Time)` — Z=1.65 for 95% service level |
| Reorder Point | `(Avg Daily Demand × Lead Time) + Safety Stock` |
| Days of Supply | `Current Stock / Avg Daily Demand` |
| Inventory Turnover | `365 / Days of Supply` |
| Stock Status | Traffic light: 🔴 Critical / 🟡 Reorder Now / 🟠 Low Stock / 🟢 Healthy |

> **Note:** Since the BigBasket dataset is a product catalogue snapshot (no transaction history), demand and stock levels are simulated using discount depth and SKU breadth as velocity proxies. Formulas follow standard FMCG supply chain methodology.

---

## Key Findings

**Catalogue EDA**
- **Beauty & Hygiene** leads SKU count (28.7%) but has the lowest avg rating — suggests over-stocking of lower-quality products
- **Eggs, Meat & Fish** has the highest avg rating with the lowest discount (10.9%) — customers buy without needing a price cut
- ~86% of SKUs are priced under ₹500 — catalogue is heavily mass-market focused
- Platform-wide avg discount is ~15% — premium categories discount significantly less
- Discount % and rating show **near-zero correlation** — quality perception is independent of pricing strategy

**Supply Chain**
- High-discount categories carry higher demand variability → larger safety stock buffers required
- Categories below the FMCG benchmark of 8x inventory turnover/year have excess working capital tied up
- Stockout risk map identifies categories with high velocity but low days of supply — priority replenishment targets

---

## Setup

### 1. Get the dataset
Download from Kaggle: [BigBasket Entire Product List](https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints)  
Rename to `bigbasket.csv` and place it in this folder.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit dashboard
```bash
streamlit run app.py
```

### 4. Run the EDA notebook
```bash
jupyter notebook bigbasket_eda_extended.ipynb
```

---

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit — BigBasket FMCG EDA + Supply Chain dashboard"
git branch -M main
git remote add origin https://github.com/goodatchess/bigbasket-eda-dashboard.git
git push -u origin main
```

---

*GitHub: [goodatchess/bigbasket-eda-dashboard](https://github.com/goodatchess/bigbasket-eda-dashboard)*
