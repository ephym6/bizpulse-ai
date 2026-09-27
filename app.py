import streamlit as st
import pandas as pd

from utils.validation import validate_sales_data
from analytics.analytics import load_and_clean, calculate_kpis, daily_revenue, top_categories, top_products
from ai.anomaly import detect_daily_revenue_anomalies
from ai.recommendations import (
    generate_recommendations,
    build_recommendation_prompt
)

st.set_page_config(page_title="BizPulse AI", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .bp-header p { color: #6b7280; font-size: 1.05rem; margin-top: 0; }
    .bp-card {
        border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 1rem 1.25rem; margin-bottom: 0.75rem; background: #ffffff;
    }
    .bp-health-score { font-size: 3rem; font-weight: 700; line-height: 1; }
    .bp-anomaly-card {
        border: 1px solid #fca5a5; background: #fef2f2;
        border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem;
    }
    .bp-insight-card {
        border: 1px solid #e5e7eb; border-radius: 10px;
        padding: 0.75rem 1rem; margin-bottom: 0.5rem; background: #fafafa;
    }
    .bp-rec-card {
        border: 1px solid #bfdbfe; background: #eff6ff;
        border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    }
    .bp-disclaimer { color: #6b7280; font-size: 0.85rem; font-style: italic; }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        white-space: normal;
        overflow-wrap: break-word;
        line-height: 1.2;
    }
    [data-testid="stMetricLabel"] {
        white-space: normal;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _format_ksh(value: float) -> str:
    """Compact currency formatting so large figures don't overflow the KPI cards."""
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"KSh {value / 1_000_000:.2f}M"
    if abs_value >= 10_000:
        return f"KSh {value / 1_000:.1f}K"
    return f"KSh {value:,.0f}"


def _to_daily_frame(series: pd.Series) -> pd.DataFrame:
    """Adapt analytics.daily_revenue()'s Series (indexed by date) into the
    Date/Revenue DataFrame shape the rest of the app (and ai/anomaly.py)
    expects. Keeping this shim here means anomaly.py and recommendations.py
    don't need to change even though the analytics engine now returns a
    Series instead of a flat DataFrame."""
    out = series.rename("Revenue").reset_index()
    out.columns = ["Date", "Revenue"]
    out["Date"] = pd.to_datetime(out["Date"])
    return out.sort_values("Date").reset_index(drop=True)


def _to_category_frame(df: pd.DataFrame) -> pd.DataFrame:
    """analytics.top_categories() now returns Category as the index with a
    Quantity column instead of Units; flatten it back to plain columns."""
    out = df.reset_index().rename(columns={"Quantity": "Units"})
    return out


def _to_product_frame(df: pd.DataFrame) -> pd.DataFrame:
    """analytics.top_products() now returns Product as the index, drops the
    Category column, renames Units to Quantity, and has no Margin % column.
    Rebuild the shape the health score / insights / recommendations code
    (and ai/recommendations.py) still expect."""
    out = df.reset_index().rename(columns={"Quantity": "Units"})
    out["Margin %"] = (out["Profit"] / out["Revenue"] * 100).where(out["Revenue"] > 0, 0)
    return out

# ------------------------------------------------------------------------
# UI-layer helpers. These live entirely in app.py (Member 3's file) rather
# than touching analytics/, ai/, or utils/ — they're derived purely from
# values those modules already return (kpis, daily, categories, products,
# anomalies), never from raw data those modules don't already expose.
# ------------------------------------------------------------------------

def _weekly_growth(daily: pd.DataFrame):
    """Week-over-week revenue growth %, or None without two full weeks of data."""
    if len(daily) < 14:
        return None
    ordered = daily.sort_values("Date")["Revenue"]
    last7 = ordered.iloc[-7:].sum()
    prev7 = ordered.iloc[-14:-7].sum()
    if prev7 == 0:
        return None
    return (last7 - prev7) / prev7 * 100


def _health_score(kpis: dict, daily: pd.DataFrame, products: pd.DataFrame, growth) -> dict:
    """
    Explainable 0-100 Business Health Score built only from kpis/daily/products
    already computed by analytics.analytics. A prototype decision-support
    indicator, not a validated financial score.
    """
    score = 0
    breakdown = {}

    if growth is None:
        rev_points, rev_flag = 15, "🟡"
    elif growth >= 5:
        rev_points, rev_flag = 25, "🟢"
    elif growth >= -5:
        rev_points, rev_flag = 15, "🟡"
    else:
        rev_points, rev_flag = 5, "🔴"
    score += rev_points
    breakdown["Revenue trend"] = rev_flag

    margin = kpis["profit_margin"]
    if margin >= 20:
        profit_points, profit_flag = 25, "🟢"
    elif margin >= 10:
        profit_points, profit_flag = 15, "🟡"
    else:
        profit_points, profit_flag = 5, "🔴"
    score += profit_points
    breakdown["Profitability"] = profit_flag

    revenue_series = daily["Revenue"]
    if len(revenue_series) >= 3 and revenue_series.mean() > 0:
        cv = revenue_series.std() / revenue_series.mean()
        if cv <= 0.3:
            consistency_points, consistency_flag = 25, "🟢"
        elif cv <= 0.6:
            consistency_points, consistency_flag = 15, "🟡"
        else:
            consistency_points, consistency_flag = 5, "🔴"
    else:
        consistency_points, consistency_flag = 15, "🟡"
    score += consistency_points
    breakdown["Sales consistency"] = consistency_flag

    total_revenue = products["Revenue"].sum()
    top2_share = (products["Revenue"].head(2).sum() / total_revenue * 100) if total_revenue else 0
    if top2_share <= 40:
        concentration_points, concentration_flag = 25, "🟢"
    elif top2_share <= 60:
        concentration_points, concentration_flag = 15, "🟡"
    else:
        concentration_points, concentration_flag = 5, "🔴"
    score += concentration_points
    breakdown["Product concentration"] = concentration_flag

    if score >= 80:
        label = "EXCELLENT"
    elif score >= 60:
        label = "GOOD"
    elif score >= 40:
        label = "NEEDS ATTENTION"
    else:
        label = "AT RISK"

    main_concern = None
    if top2_share > 40:
        main_concern = f"{top2_share:.0f}% of your revenue comes from only two products."
    elif margin < 10:
        main_concern = f"Profit margin is only {margin:.1f}% — a thin cushion against cost or price shocks."
    elif growth is not None and growth < -5:
        main_concern = f"Revenue dropped {abs(growth):.0f}% week-over-week."

    return {"score": score, "label": label, "breakdown": breakdown, "main_concern": main_concern}


def _insights(kpis: dict, daily: pd.DataFrame, categories: pd.DataFrame, products: pd.DataFrame, growth) -> list:
    """Rule-based insight feed built only from kpis/daily/categories/products."""
    insights = []

    if growth is not None:
        if growth >= 5:
            insights.append(("📈", "Sales Growth", f"Revenue increased {growth:.0f}% this week compared with last week."))
        elif growth <= -5:
            insights.append(("📉", "Sales Decline", f"Revenue decreased {abs(growth):.0f}% this week compared with last week."))

    total_revenue = products["Revenue"].sum()
    if total_revenue > 0 and not products.empty:
        top = products.iloc[0]
        top_share = top["Revenue"] / total_revenue * 100
        if top_share >= 15:
            insights.append(("🔥", "High Performer", f"{top['Product']} contributes {top_share:.0f}% of total revenue."))

    if len(products) >= 2:
        median_margin = products["Margin %"].median()
        high_volume = products.sort_values("Units", ascending=False).head(3)
        candidates = high_volume[high_volume["Margin %"] < median_margin - 5]
        if not candidates.empty:
            row = candidates.iloc[0]
            insights.append(("💰", "Margin Opportunity", f"{row['Product']} sells frequently but has a significantly lower profit margin than similar products."))

    if not categories.empty:
        top_cat = categories.iloc[0]
        cat_total = categories["Revenue"].sum()
        if cat_total > 0:
            cat_share = top_cat["Revenue"] / cat_total * 100
            if cat_share >= 30:
                insights.append(("🏷️", "Category Leader", f"{top_cat['Category']} makes up {cat_share:.0f}% of total revenue."))

    return insights[:5]


# ------------------------------------------------------------------------
# Page
# ------------------------------------------------------------------------

st.markdown(
    '<div class="bp-header"><h1>📊 BizPulse AI</h1>'
    '<p>Turn your business data into better decisions.</p></div>',
    unsafe_allow_html=True,
)

st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader("Upload sales CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample dataset", value=uploaded_file is None)
with open("data/sample_sales.csv", "rb") as f:
    st.sidebar.download_button(
        "⬇️ Download sample CSV", data=f.read(),
        file_name="bizpulse_sample_sales.csv", mime="text/csv",
        use_container_width=True,
    )

try:
    # load_and_clean() (new analytics API) takes a path/file-like object and
    # does its own pd.read_csv + column-alias detection internally, but we
    # still need a raw preview/validation pass first, so read once for that
    # and rewind the uploaded file before handing it to load_and_clean().
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        clean_source = uploaded_file
    elif use_sample:
        raw_df = pd.read_csv("data/sample_sales.csv")
        clean_source = "data/sample_sales.csv"
    else:
        st.info("Upload a CSV file to begin, or tick **Use sample dataset** in the sidebar.")
        st.stop()

    is_valid, errors = validate_sales_data(raw_df)
    if not is_valid:
        st.error("The uploaded file has validation errors:")
        for error in errors:
            st.write(f"- {error}")
        st.stop()

    with st.expander("Preview uploaded data", expanded=False):
        st.dataframe(raw_df.head(10), use_container_width=True)

    if uploaded_file is not None:
        uploaded_file.seek(0)
    df = load_and_clean(clean_source)

    kpis = calculate_kpis(df)
    daily = _to_daily_frame(daily_revenue(df))
    categories = _to_category_frame(top_categories(df))
    # top_products() defaults to the top 5 by revenue; the health score and
    # insight logic below need every product to get accurate concentration
    # and total-revenue figures, so ask for all of them explicitly.
    products = _to_product_frame(top_products(df, n=df["Product"].nunique()))
    anomalies = detect_daily_revenue_anomalies(daily)

    growth = _weekly_growth(daily)
    health = _health_score(kpis, daily, products, growth)
    insights = _insights(kpis, daily, categories, products, growth)

    st.divider()

    # ---- KPI row ----
    st.subheader("Business Overview")
    growth_display = f"{growth:+.1f}%" if growth is not None else "N/A"

    row1 = st.columns(3)
    row1[0].metric("Revenue", _format_ksh(kpis["total_revenue"]))
    row1[1].metric("Profit", _format_ksh(kpis["total_profit"]))
    row1[2].metric("Profit Margin", f"{kpis['profit_margin']:.1f}%")

    row2 = st.columns(3)
    row2[0].metric("Units Sold", f"{kpis['units_sold']:,.0f}")
    row2[1].metric("Revenue Growth (WoW)", growth_display)
    # row2[2] left empty intentionally to keep card widths consistent with row1

    st.caption(f"Top product: **{kpis['top_product']}**  •  Top category: **{kpis['top_category']}**")

    st.divider()

    # ---- Health score + charts ----
    left, right = st.columns([1, 2])
    with left:
        st.subheader("Business Health")
        st.markdown(
            f'<div class="bp-card">'
            f'<div class="bp-health-score" style="color:#111827;">{health["score"]}/100</div>'
            f'<div style="color:#6b7280;">{health["label"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for label, flag in health["breakdown"].items():
            st.write(f"{flag} {label}")
        if health["main_concern"]:
            st.warning(f"**Main concern:** {health['main_concern']}")
        st.caption("Prototype decision-support indicator calculated from defined metrics — not a validated financial score.")

    with right:
        st.subheader("Trends")
        tab1, tab2, tab3 = st.tabs(["Revenue Over Time", "Revenue by Category", "Top Products"])
        with tab1:
            st.line_chart(daily.set_index("Date")["Revenue"])
        with tab2:
            st.bar_chart(categories.set_index("Category")["Revenue"])
        with tab3:
            st.dataframe(products.head(10), use_container_width=True)

    st.divider()

    # ---- Insights + Anomaly ----
    ins_col, anom_col = st.columns([1.4, 1])
    with ins_col:
        st.subheader("Automatic Insights")
        if insights:
            for icon, title, body in insights:
                st.markdown(
                    f'<div class="bp-insight-card">'
                    f'<strong style="color:#111827;">{icon} {title}</strong><br>'
                    f'<span style="color:#374151;">{body}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No notable patterns detected yet — insights improve as more data accumulates.")

    with anom_col:
        st.subheader("Anomaly Alerts")
        if anomalies.empty:
            st.success("No major daily revenue anomalies detected.")
        else:
            for _, row in anomalies.iterrows():
                st.markdown(
                    f'<div class="bp-anomaly-card">'
                    f'<strong style="color:#7f1d1d;">🚨 Anomaly detected</strong><br>'
                    f'<span style="color:#7f1d1d;">{row["Date"].date()}: revenue was KSh {row["Revenue"]:,.0f} '
                    f'(z-score {row["z_score"]:.2f}).</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ---- AI Recommendations ----
    st.subheader("AI Business Advisor")
    recommendations = generate_recommendations(
        kpis,
        categories,
        products,
        anomalies
    )
    st.caption(
        "Recommendations are generated from verified, aggregated "
        "business metrics. If the AI service is unavailable, "
        "BizPulse automatically falls back to analytics-driven guidance."
    )
    for i, rec in enumerate(recommendations, start=1):
        st.markdown(
            f'<div class="bp-rec-card">'
            f'<strong style="color:#1e3a8a;">{i}.</strong> '
            f'<span style="color:#1e3a8a;">{rec}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with st.expander("Show LLM-ready prompt"):
        st.code(build_recommendation_prompt(kpis, categories, products, anomalies))

    st.markdown(
        '<p class="bp-disclaimer">AI recommendations are decision-support suggestions and should be reviewed by the '
        'business owner before action is taken. Only aggregated business indicators — never customer names, phone '
        'numbers, or payment details — are sent to the AI model.</p>',
        unsafe_allow_html=True,
    )

except FileNotFoundError:
    st.error("Sample dataset not found.")
except Exception as exc:
    st.exception(exc)