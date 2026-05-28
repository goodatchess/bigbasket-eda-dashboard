# BigBasket FMCG — EDA & Analytics Dashboard

Exploratory data analysis and interactive Streamlit dashboard for BigBasket's grocery catalogue — 27,555 SKUs across 11 categories and 90 sub-categories.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Pandas](https://img.shields.io/badge/Pandas-EDA-green) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red) ![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-orange)

---

## What's inside

| File | What it does |
|------|-------------|
| `bigbasket_eda.ipynb` | Full EDA notebook — cleaning, KPIs, 9 charts, insights |
| `app.py` | Streamlit dashboard — 5 tabs, 11 charts, sidebar filters |
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

---

## Key Findings

1. **Beauty & Hygiene** leads SKU count (28.7%) but has the lowest avg rating — suggests over-stocking of lower-quality products
2. **Eggs, Meat & Fish** has the highest avg rating with the lowest discount (10.9%) — customers buy it without needing a price cut
3. **~86% of SKUs are priced under ₹500** — catalogue is heavily mass-market focused
4. Platform-wide avg discount is **~15%** — premium categories discount significantly less
5. Discount % and rating show **near-zero correlation** — quality perception is independent of pricing strategy

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
jupyter notebook bigbasket_eda.ipynb
```

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — BigBasket EDA and Streamlit dashboard"
git branch -M main
git remote add origin https://github.com/goodatchess/bigbasket-eda-dashboard.git
git push -u origin main
```

---

*Dataset: [Kaggle — surajjha101](https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints)*
