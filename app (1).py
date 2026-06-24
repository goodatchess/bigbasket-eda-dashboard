"""
BigBasket FMCG — Streamlit Analytics Dashboard
GitHub: https://github.com/goodatchess/bigbasket-eda-dashboard

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="BigBasket FMCG Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1a1a2e; }
    section[data-testid="stSidebar"] * { color: #c0c0d0 !important; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #1e1e2e;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="metric-container"] label { color: #888 !important; font-size: 12px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #e0e0e0 !important; font-size: 26px !important; font-weight: 700 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] { font-size: 11px !important; }

    /* Headers */
    h1, h2, h3 { color: #e0e0e0 !important; }

    /* Divider */
    hr { border-color: #2a2a4a; }

    /* Plot backgrounds */
    .element-container { background: transparent; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { background: #1e1e2e; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #888; border-radius: 6px; }
    .stTabs [aria-selected="true"] { background: #2a2a4a !important; color: #fff !important; }

    /* Insight boxes */
    .insight-box {
        background: #1e1e2e;
        border-left: 3px solid #3b6d11;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 13px;
        color: #c0c0d0;
    }
</style>
""", unsafe_allow_html=True)

# ── Seaborn / Matplotlib dark theme ───────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  '#1e1e2e',
    'axes.facecolor':    '#1e1e2e',
    'axes.edgecolor':    '#333',
    'axes.labelcolor':   '#aaa',
    'xtick.color':       '#aaa',
    'ytick.color':       '#aaa',
    'text.color':        '#ddd',
    'grid.color':        '#2a2a4a',
    'grid.linewidth':    0.6,
    'font.size':         10,
    'axes.spines.top':   False,
    'axes.spines.right': False,
})
sns.set_palette("husl")

CAT_COLORS = ["#7f77dd","#185fa5","#3b6d11","#1d9e75",
              "#d85a30","#ba7517","#854f0b","#3c3489",
              "#c0392b","#8e44ad","#16a085","#e67e22"]

# ── Data loading ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('bigbasket.csv')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df.dropna(subset=['sale_price', 'market_price'])
    df = df[df['sale_price'] <= df['market_price']]
    df['discount_pct'] = ((df['market_price'] - df['sale_price']) / df['market_price'] * 100).round(2)

    def price_tier(p):
        if p < 100:   return 'Budget (<₹100)'
        elif p < 500: return 'Mid (₹100–500)'
        else:         return 'Premium (₹500+)'
    df['price_tier'] = df['sale_price'].apply(price_tier)

    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    return df

# ── Sidebar filters ───────────────────────────────────────────────
def sidebar(df):
    st.sidebar.markdown("## 🛒 BigBasket Analytics")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")

    cats = ['All'] + sorted(df['category'].dropna().unique().tolist())
    sel_cat = st.sidebar.selectbox("Category", cats)

    tiers = ['All', 'Budget (<₹100)', 'Mid (₹100–500)', 'Premium (₹500+)']
    sel_tier = st.sidebar.selectbox("Price Tier", tiers)

    if 'rating' in df.columns:
        min_r, max_r = float(df['rating'].min()), float(df['rating'].max())
        sel_rating = st.sidebar.slider("Min Rating", min_r, max_r, min_r, 0.1)
    else:
        sel_rating = None

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown("**Dataset:** 27,555 SKUs · 11 categories")
    st.sidebar.markdown("**Source:** [Kaggle](https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints)")
    st.sidebar.markdown("**GitHub:** [goodatchess](https://github.com/goodatchess/bigbasket-eda-dashboard)")

    return sel_cat, sel_tier, sel_rating


def apply_filters(df, cat, tier, rating):
    fdf = df.copy()
    if cat  != 'All': fdf = fdf[fdf['category'] == cat]
    if tier != 'All': fdf = fdf[fdf['price_tier'] == tier]
    if rating and 'rating' in fdf.columns:
        fdf = fdf[fdf['rating'] >= rating]
    return fdf

# ── KPI row ───────────────────────────────────────────────────────
def show_kpis(df, full_df):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    pct_change = lambda a, b: f"{((a-b)/b*100):+.1f}%" if b else "—"

    c1.metric("Total SKUs",     f"{len(df):,}",
              pct_change(len(df), len(full_df)))
    c2.metric("Avg MRP",        f"₹{df['market_price'].mean():.0f}")
    c3.metric("Avg Sale Price", f"₹{df['sale_price'].mean():.0f}",
              f"-₹{(df['market_price'].mean() - df['sale_price'].mean()):.0f} off MRP")
    c4.metric("Avg Discount",   f"{df['discount_pct'].mean():.1f}%")
    c5.metric("Avg Rating",
              f"{df['rating'].mean():.2f} ⭐" if 'rating' in df.columns else "N/A")
    c6.metric("Unique Brands",
              f"{df['brand'].nunique():,}" if 'brand' in df.columns else "N/A")

# ── Chart helpers ─────────────────────────────────────────────────
def hbar(data, title, xlabel, colors=None, fmt=None):
    fig, ax = plt.subplots(figsize=(7, max(3, len(data) * 0.45)))
    c = colors if colors else CAT_COLORS[:len(data)]
    bars = ax.barh(data.index, data.values, color=c, edgecolor='none')
    labels = [fmt(v) for v in data.values] if fmt else [str(v) for v in data.values]
    ax.bar_label(bars, labels=labels, padding=4, fontsize=8, color='#ddd')
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
    ax.invert_yaxis()
    ax.grid(axis='x')
    fig.tight_layout()
    return fig

# ── Tab 1: Overview ───────────────────────────────────────────────
def tab_overview(df):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### SKU Count by Category")
        sku = df['category'].value_counts().head(11)
        pcts = (sku / sku.sum() * 100).round(1)
        fig = hbar(sku, "", "Number of SKUs", CAT_COLORS[:len(sku)],
                   fmt=lambda v: f"{v:,}")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c2:
        st.markdown("#### Price Tier Split")
        tier_counts = df['price_tier'].value_counts()
        fig, ax = plt.subplots(figsize=(5, 4))
        wedges, texts, autotexts = ax.pie(
            tier_counts, labels=tier_counts.index,
            autopct='%1.1f%%', startangle=140,
            wedgeprops=dict(width=0.55),
            colors=['#3b6d11', '#185fa5', '#7f77dd']
        )
        for t in texts:     t.set_fontsize(9);  t.set_color('#ddd')
        for t in autotexts: t.set_fontsize(9);  t.set_color('#111')
        ax.set_title("SKUs by Price Tier", fontsize=11, fontweight='bold')
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Sale Price Distribution")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        data = df[df['sale_price'] <= 2000]['sale_price']
        ax.hist(data, bins=50, color='#185fa5', edgecolor='#0f1117', linewidth=0.3)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{int(x)}'))
        ax.set_xlabel("Sale Price")
        ax.set_ylabel("SKU Count")
        ax.set_title("Sale Price Distribution (≤₹2000)", fontsize=11, fontweight='bold')
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c4:
        st.markdown("#### Sub-category Count (Top 12)")
        if 'sub_category' in df.columns:
            sub = df['sub_category'].value_counts().head(12)
            fig = hbar(sub, "", "SKU Count", fmt=lambda v: f"{v:,}")
            st.pyplot(fig, use_container_width=True)
            plt.close()
        else:
            st.info("No sub_category column found.")

# ── Tab 2: Pricing & Discounts ────────────────────────────────────
def tab_pricing(df):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Avg Discount by Category")
        disc = df.groupby('category')['discount_pct'].mean().sort_values(ascending=False)
        colors = ['#e74c3c' if v > 17 else '#e67e22' if v > 13 else '#2ecc71' for v in disc.values]
        fig = hbar(disc, "", "Avg Discount %", colors, fmt=lambda v: f"{v:.1f}%")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c2:
        st.markdown("#### MRP vs Sale Price by Category")
        cat_price = df.groupby('category')[['market_price', 'sale_price']].mean().sort_values('market_price', ascending=True)
        fig, ax = plt.subplots(figsize=(7, max(3, len(cat_price) * 0.45)))
        y = np.arange(len(cat_price))
        ax.barh(y, cat_price['market_price'], color='#e74c3c', alpha=0.6, label='Avg MRP', edgecolor='none')
        ax.barh(y, cat_price['sale_price'],   color='#2ecc71', alpha=0.9, label='Avg Sale', edgecolor='none')
        ax.set_yticks(y)
        ax.set_yticklabels(cat_price.index, fontsize=8)
        ax.set_xlabel("Price (₹)")
        ax.set_title("Avg MRP vs Avg Sale Price", fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Discount Distribution (Histogram)")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.hist(df['discount_pct'], bins=40, color='#d85a30', edgecolor='#0f1117', linewidth=0.3)
        ax.set_xlabel("Discount %")
        ax.set_ylabel("SKU Count")
        ax.set_title("Discount % Distribution across all SKUs", fontsize=11, fontweight='bold')
        ax.axvline(df['discount_pct'].mean(), color='#f1c40f', linewidth=1.5,
                   linestyle='--', label=f"Mean: {df['discount_pct'].mean():.1f}%")
        ax.legend(fontsize=9)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c4:
        st.markdown("#### Price Tier × Category Heatmap")
        if 'sub_category' not in df.columns:
            st.info("Need sub_category column.")
        else:
            pivot = df.groupby(['category', 'price_tier'])['discount_pct'].mean().unstack(fill_value=0)
            fig, ax = plt.subplots(figsize=(7, max(3.5, len(pivot) * 0.5)))
            sns.heatmap(pivot, ax=ax, cmap='RdYlGn_r', annot=True, fmt='.1f',
                        linewidths=0.4, linecolor='#0f1117',
                        cbar_kws={'label': 'Avg Discount %'}, annot_kws={'size': 8})
            ax.set_title("Avg Discount % — Category × Price Tier", fontsize=11, fontweight='bold')
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.tick_params(labelsize=8)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

# ── Tab 3: Ratings ────────────────────────────────────────────────
def tab_ratings(df):
    if 'rating' not in df.columns:
        st.warning("No rating column in dataset.")
        return

    rdf = df.dropna(subset=['rating'])

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Avg Rating by Category")
        rat = rdf.groupby('category')['rating'].mean().sort_values(ascending=False)
        colors = ['#2ecc71' if r >= 4.0 else '#e67e22' if r >= 3.8 else '#e74c3c' for r in rat.values]
        fig = hbar(rat, "", "Avg Rating", colors, fmt=lambda v: f"{v:.2f}")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c2:
        st.markdown("#### Rating Distribution (Top 5 Categories)")
        top5 = rdf['category'].value_counts().head(5).index.tolist()
        fig, ax = plt.subplots(figsize=(7, 4))
        data_plot = [rdf[rdf['category'] == c]['rating'].dropna().values for c in top5]
        vp = ax.violinplot(data_plot, positions=range(len(top5)), showmedians=True,
                           showextrema=False)
        for i, body in enumerate(vp['bodies']):
            body.set_facecolor(CAT_COLORS[i])
            body.set_alpha(0.7)
        vp['cmedians'].set_color('#fff')
        vp['cmedians'].set_linewidth(1.5)
        ax.set_xticks(range(len(top5)))
        ax.set_xticklabels([c[:14] for c in top5], fontsize=8, rotation=15)
        ax.set_ylabel("Rating")
        ax.set_title("Rating Distribution — Top 5 Categories", fontsize=11, fontweight='bold')
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### Discount % vs Rating (Scatter)")
        sample = rdf[['discount_pct', 'rating']].dropna().sample(min(2000, len(rdf)), random_state=42)
        corr = sample.corr().loc['discount_pct', 'rating']
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.scatter(sample['discount_pct'], sample['rating'],
                   alpha=0.15, s=8, color='#185fa5')
        m, b = np.polyfit(sample['discount_pct'], sample['rating'], 1)
        x_line = np.linspace(sample['discount_pct'].min(), sample['discount_pct'].max(), 100)
        ax.plot(x_line, m * x_line + b, color='#e74c3c', linewidth=1.5,
                label=f'Trend (r={corr:.2f})')
        ax.set_xlabel("Discount %")
        ax.set_ylabel("Rating")
        ax.set_title("Discount % vs Customer Rating", fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c4:
        st.markdown("#### Value Score — Cheapest per Rating Point (Top 15)")
        vdf = rdf[rdf['rating'] > 0].copy()
        vdf['value_score'] = (vdf['sale_price'] / vdf['rating']).round(2)
        if 'product' in vdf.columns:
            best = vdf.nsmallest(15, 'value_score')[['product', 'sale_price', 'rating', 'value_score']]
            best['product'] = best['product'].str[:30]
            best = best.set_index('product')
            fig = hbar(best['value_score'], "", "₹ per Rating Point",
                       fmt=lambda v: f"₹{v:.0f}")
            st.pyplot(fig, use_container_width=True)
            plt.close()
        else:
            st.info("No product column found.")

# ── Tab 4: Brands ─────────────────────────────────────────────────
def tab_brands(df):
    if 'brand' not in df.columns:
        st.warning("No brand column found.")
        return

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Top 15 Brands by SKU Count")
        top = df['brand'].value_counts().head(15)
        fig = hbar(top, "", "SKU Count", fmt=lambda v: f"{v:,}")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c2:
        st.markdown("#### Top 15 Brands by Avg Discount")
        top_brands = df['brand'].value_counts().head(30).index
        bd = df[df['brand'].isin(top_brands)].groupby('brand')['discount_pct'].mean().sort_values(ascending=False).head(15)
        colors = ['#e74c3c' if v > 17 else '#e67e22' if v > 13 else '#2ecc71' for v in bd.values]
        fig = hbar(bd, "", "Avg Discount %", colors, fmt=lambda v: f"{v:.1f}%")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    st.markdown("#### Brand Deep-Dive")
    top50 = df['brand'].value_counts().head(50).index.tolist()
    sel_brand = st.selectbox("Select a brand", top50)
    bdf = df[df['brand'] == sel_brand]

    bc1, bc2, bc3, bc4 = st.columns(4)
    bc1.metric("SKUs",         f"{len(bdf):,}")
    bc2.metric("Avg MRP",      f"₹{bdf['market_price'].mean():.0f}")
    bc3.metric("Avg Sale",     f"₹{bdf['sale_price'].mean():.0f}")
    bc4.metric("Avg Discount", f"{bdf['discount_pct'].mean():.1f}%")

    if 'sub_category' in bdf.columns:
        st.markdown(f"**Sub-categories for {sel_brand}:**")
        sub_counts = bdf['sub_category'].value_counts().head(10)
        fig = hbar(sub_counts, "", "SKU Count", fmt=lambda v: f"{v:,}")
        st.pyplot(fig, use_container_width=True)
        plt.close()

# ── Tab 5: Bubble chart ───────────────────────────────────────────
def tab_bubble(df):
    st.markdown("#### Category Bubble Chart — SKU Count vs Avg Rating (bubble = avg discount)")
    if 'rating' not in df.columns:
        st.warning("No rating column.")
        return

    cat_stats = df.groupby('category').agg(
        sku_count=('sale_price', 'count'),
        avg_rating=('rating', 'mean'),
        avg_discount=('discount_pct', 'mean'),
        avg_sale=('sale_price', 'mean')
    ).dropna().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        cat_stats['sku_count'],
        cat_stats['avg_rating'],
        s=cat_stats['avg_discount'] * 60,
        c=CAT_COLORS[:len(cat_stats)],
        alpha=0.85,
        edgecolors='white',
        linewidths=0.6
    )
    for _, row in cat_stats.iterrows():
        ax.annotate(row['category'][:14],
                    (row['sku_count'], row['avg_rating']),
                    textcoords="offset points", xytext=(6, 4),
                    fontsize=7.5, color='#ddd')
    ax.set_xlabel("SKU Count")
    ax.set_ylabel("Avg Rating")
    ax.set_title("SKU Count vs Avg Rating  (bubble size = avg discount %)",
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    st.markdown("---")
    st.markdown("#### Key Insights")
    insights = [
        "🟢 <b>Beauty & Hygiene</b> has the most SKUs (28.7%) but the lowest avg rating — possible over-stocking of lower-quality products.",
        "🟢 <b>Eggs, Meat & Fish</b> has the highest avg rating with the lowest discount — customers buy it without needing a price cut.",
        "🟡 <b>~86% of SKUs</b> are priced under ₹500 — catalogue is heavily mass-market focused.",
        "🟡 Platform-wide avg discount is <b>~15%</b> — premium categories discount significantly less.",
        "🔵 Discount % and rating show <b>near-zero correlation</b> — quality perception is independent of pricing strategy.",
    ]
    for ins in insights:
        st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)


# ── Tab 6: Supply Chain Intelligence ─────────────────────────────
def tab_supply_chain(df):
    st.markdown("#### 🏭 Supply Chain Intelligence — Category-Level Inventory Analysis")
    st.markdown("*Simulated inventory parameters derived from catalogue velocity and discount signals.*")

    # ── Build SC metrics per category ────────────────────────────
    cat_stats = df.groupby('category').agg(
        sku_count    = ('sale_price', 'count'),
        avg_discount = ('discount_pct', 'mean'),
        avg_price    = ('sale_price', 'mean'),
        avg_rating   = ('rating', 'mean') if 'rating' in df.columns else ('sale_price', 'count'),
    ).reset_index()

    np.random.seed(42)

    # Demand velocity: normalised SKU count weighted by discount (high disc = high sell-through)
    cat_stats['velocity_score'] = (
        (cat_stats['sku_count'] / cat_stats['sku_count'].max()) * 0.6 +
        (cat_stats['avg_discount'] / cat_stats['avg_discount'].max()) * 0.4
    ).round(3)

    # Simulated avg daily demand units (50–500 range, velocity-driven)
    cat_stats['avg_daily_demand'] = (50 + cat_stats['velocity_score'] * 450).round(0).astype(int)

    # Simulated demand std dev (higher discount = more variable demand)
    cat_stats['demand_std'] = (cat_stats['avg_daily_demand'] * 0.15 +
                                cat_stats['avg_discount'] * 0.8).round(1)

    # Lead time: 2–5 days (premium = longer, budget = shorter supply chain)
    cat_stats['lead_time_days'] = np.where(cat_stats['avg_price'] > 500, 5,
                                   np.where(cat_stats['avg_price'] > 100, 3, 2))

    # Safety Stock = Z * σ_demand * sqrt(lead_time)  [Z=1.65 for 95% service level]
    Z = 1.65
    cat_stats['safety_stock'] = (Z * cat_stats['demand_std'] *
                                  np.sqrt(cat_stats['lead_time_days'])).round(0).astype(int)

    # Reorder Point = (avg_daily_demand * lead_time) + safety_stock
    cat_stats['reorder_point'] = (
        cat_stats['avg_daily_demand'] * cat_stats['lead_time_days'] +
        cat_stats['safety_stock']
    ).astype(int)

    # Simulated current stock (some categories near/below ROP to show risk)
    cat_stats['current_stock'] = (
        cat_stats['reorder_point'] * np.random.uniform(0.6, 2.2, len(cat_stats))
    ).round(0).astype(int)

    # Days of Supply = current_stock / avg_daily_demand
    cat_stats['days_of_supply'] = (
        cat_stats['current_stock'] / cat_stats['avg_daily_demand']
    ).round(1)

    # Inventory Turnover (proxy, annualised) = 365 / DOS
    cat_stats['inventory_turnover'] = (365 / cat_stats['days_of_supply']).round(1)

    # Stockout Risk
    def risk_flag(row):
        if row['current_stock'] <= row['safety_stock']:         return '🔴 Critical'
        elif row['current_stock'] <= row['reorder_point']:      return '🟡 Reorder Now'
        elif row['days_of_supply'] < 5:                         return '🟠 Low Stock'
        else:                                                    return '🟢 Healthy'
    cat_stats['stock_status'] = cat_stats.apply(risk_flag, axis=1)

    # ── KPI summary row ───────────────────────────────────────────
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    critical = (cat_stats['stock_status'] == '🔴 Critical').sum()
    reorder  = (cat_stats['stock_status'] == '🟡 Reorder Now').sum()
    avg_dos  = cat_stats['days_of_supply'].mean()
    avg_turn = cat_stats['inventory_turnover'].mean()

    k1.metric("🔴 Critical Stock",   f"{critical} categories")
    k2.metric("🟡 Reorder Needed",   f"{reorder} categories")
    k3.metric("Avg Days of Supply",  f"{avg_dos:.1f} days")
    k4.metric("Avg Inventory Turns", f"{avg_turn:.1f}x / year")
    st.markdown("---")

    # ── Main table ────────────────────────────────────────────────
    st.markdown("#### 📋 Category Inventory Status")
    display_cols = ['category', 'avg_daily_demand', 'safety_stock', 'reorder_point',
                    'current_stock', 'days_of_supply', 'inventory_turnover', 'stock_status']
    display_df = cat_stats[display_cols].sort_values('days_of_supply').copy()
    display_df.columns = ['Category', 'Avg Daily Demand', 'Safety Stock',
                          'Reorder Point', 'Current Stock',
                          'Days of Supply', 'Inv. Turnover (x/yr)', 'Status']
    st.dataframe(display_df.set_index('Category'), use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    # ── Chart 1: Days of Supply by Category ──────────────────────
    with c1:
        st.markdown("#### Days of Supply by Category")
        dos = cat_stats.set_index('category')['days_of_supply'].sort_values()
        colors = ['#e74c3c' if v < 3 else '#e67e22' if v < 6 else '#2ecc71' for v in dos.values]
        fig, ax = plt.subplots(figsize=(7, max(3, len(dos) * 0.45)))
        bars = ax.barh(dos.index, dos.values, color=colors, edgecolor='none')
        ax.bar_label(bars, labels=[f"{v:.1f}d" for v in dos.values], padding=4, fontsize=8, color='#ddd')
        ax.axvline(3, color='#e74c3c', lw=1.2, ls='--', label='Critical (<3d)')
        ax.axvline(6, color='#e67e22', lw=1.2, ls='--', label='Low (<6d)')
        ax.set_xlabel("Days of Supply")
        ax.set_title("Days of Supply — by Category", fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(axis='x', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── Chart 2: Reorder Point vs Current Stock ───────────────────
    with c2:
        st.markdown("#### Current Stock vs Reorder Point")
        cs = cat_stats.sort_values('days_of_supply')
        x = np.arange(len(cs))
        fig, ax = plt.subplots(figsize=(7, max(3, len(cs) * 0.45)))
        ax.barh(x - 0.2, cs['current_stock'],  height=0.35, color='#185fa5', label='Current Stock')
        ax.barh(x + 0.2, cs['reorder_point'],  height=0.35, color='#e67e22', label='Reorder Point', alpha=0.8)
        ax.set_yticks(x)
        ax.set_yticklabels(cs['category'], fontsize=8)
        ax.set_xlabel("Units")
        ax.set_title("Current Stock vs Reorder Point", fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(axis='x', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    c3, c4 = st.columns(2)

    # ── Chart 3: Inventory Turnover ───────────────────────────────
    with c3:
        st.markdown("#### Inventory Turnover (x/year)")
        it = cat_stats.set_index('category')['inventory_turnover'].sort_values(ascending=False)
        colors_it = ['#2ecc71' if v >= 12 else '#e67e22' if v >= 6 else '#e74c3c' for v in it.values]
        fig, ax = plt.subplots(figsize=(7, max(3, len(it) * 0.45)))
        bars = ax.barh(it.index, it.values, color=colors_it, edgecolor='none')
        ax.bar_label(bars, labels=[f"{v:.1f}x" for v in it.values], padding=4, fontsize=8, color='#ddd')
        ax.axvline(8, color='#2ecc71', lw=1.2, ls='--', label='FMCG benchmark (8x)')
        ax.set_xlabel("Turnover (times/year)")
        ax.set_title("Inventory Turnover by Category", fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── Chart 4: Velocity Score vs Stockout Risk ──────────────────
    with c4:
        st.markdown("#### Demand Velocity vs Days of Supply")
        fig, ax = plt.subplots(figsize=(7, 4))
        color_map = {'🔴 Critical': '#e74c3c', '🟡 Reorder Now': '#f39c12',
                     '🟠 Low Stock': '#e67e22', '🟢 Healthy': '#2ecc71'}
        for status, grp in cat_stats.groupby('stock_status'):
            ax.scatter(grp['velocity_score'], grp['days_of_supply'],
                       color=color_map.get(status, '#aaa'), label=status, s=100, edgecolors='white', lw=0.5)
            for _, row in grp.iterrows():
                ax.annotate(row['category'][:12], (row['velocity_score'], row['days_of_supply']),
                            textcoords='offset points', xytext=(5, 3), fontsize=7, color='#ccc')
        ax.axhline(3, color='#e74c3c', lw=1, ls='--', alpha=0.6)
        ax.set_xlabel("Demand Velocity Score")
        ax.set_ylabel("Days of Supply")
        ax.set_title("Velocity vs DOS — Stockout Risk Map", fontsize=11, fontweight='bold')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("---")
    st.markdown("#### 💡 Supply Chain Insights")
    sc_insights = [
        "🔴 Categories with <b>high velocity + low DOS</b> are at immediate stockout risk — priority replenishment needed.",
        "🟡 <b>Safety stock</b> calculated at 95% service level (Z=1.65) — buffers against demand variability and lead time uncertainty.",
        "🟢 FMCG benchmark inventory turnover is <b>8–12x/year</b> — categories below this have working capital tied up unnecessarily.",
        "🔵 <b>Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock</b> — trigger purchase orders when stock hits this level.",
        "🟡 High-discount categories show <b>higher demand variability</b> — requiring larger safety stock buffers.",
    ]
    for ins in sc_insights:
        st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────
def main():
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("❌ `bigbasket.csv` not found. Place it in the same folder and run again.")
        st.markdown("[Download from Kaggle](https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints)")
        st.stop()

    sel_cat, sel_tier, sel_rating = sidebar(df)
    fdf = apply_filters(df, sel_cat, sel_tier, sel_rating)

    # Header
    st.markdown("## 🛒 BigBasket FMCG Analytics Dashboard")
    st.markdown(f"Showing **{len(fdf):,}** of {len(df):,} SKUs · Filtered by: `{sel_cat}` · `{sel_tier}`")
    st.markdown("---")

    # KPIs
    show_kpis(fdf, df)
    st.markdown("---")

    # Tabs
    t1, t2, t3, t4, t5, t6 = st.tabs(["📦 Overview", "💰 Pricing & Discounts", "⭐ Ratings", "🏷️ Brands", "🔵 Bubble Chart", "🏭 Supply Chain"])

    with t1: tab_overview(fdf)
    with t2: tab_pricing(fdf)
    with t3: tab_ratings(fdf)
    with t4: tab_brands(fdf)
    with t5: tab_bubble(fdf)
    with t6: tab_supply_chain(fdf)


if __name__ == '__main__':
    main()
