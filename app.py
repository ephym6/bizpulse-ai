import streamlit as st
import pandas as pd

from utils.validation import validate_sales_data
from analytics.analytics import prepare_sales_data, calculate_kpis, build_daily_revenue, build_category_summary, build_product_summary
from ai.anomaly import detect_daily_revenue_anomalies
from ai.recommendations import generate_fallback_recommendations, build_recommendation_prompt

st.set_page_config(page_title="BizPulse AI", page_icon="📊", layout="wide")

st.title("📊 BizPulse AI")
st.caption("Turn your business data into better decisions.")

st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader("Upload sales CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample dataset", value=uploaded_file is None)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif use_sample:
        df = pd.read_csv("data/sample_sales.csv")
    else:
        st.info("Upload a CSV file to begin.")
        st.stop()

    is_valid, errors = validate_sales_data(df)
    if not is_valid:
        st.error("The uploaded file has validation errors:")
        for error in errors:
            st.write(f"- {error}")
        st.stop()

    df = prepare_sales_data(df)

    kpis = calculate_kpis(df)
    daily = build_daily_revenue(df)
    categories = build_category_summary(df)
    products = build_product_summary(df)
    anomalies = detect_daily_revenue_anomalies(daily)

    st.subheader("Business Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", f"KSh {kpis['total_revenue']:,.0f}")
    c2.metric("Profit", f"KSh {kpis['total_profit']:,.0f}")
    c3.metric("Profit Margin", f"{kpis['profit_margin']:.1f}%")
    c4.metric("Units Sold", f"{kpis['units_sold']:,.0f}")
    c5.metric("Top Product", kpis["top_product"])

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue Over Time")
        st.line_chart(daily.set_index("Date")["Revenue"])

    with right:
        st.subheader("Revenue by Category")
        st.bar_chart(categories.set_index("Category")["Revenue"])

    st.subheader("Top Products")
    st.dataframe(products.head(10), use_container_width=True)

    st.subheader("Automatic Insights")
    insights = [
        f"Top-selling product: {kpis['top_product']}.",
        f"Overall profit margin: {kpis['profit_margin']:.1f}%.",
        f"Highest-revenue category: {kpis['top_category']}.",
    ]
    for insight in insights:
        st.write(f"• {insight}")

    st.subheader("Anomaly Alerts")
    if anomalies.empty:
        st.success("No major daily revenue anomalies detected.")
    else:
        for _, row in anomalies.iterrows():
            st.warning(
                f"{row['Date'].date()}: revenue was KSh {row['Revenue']:,.0f} "
                f"(z-score {row['z_score']:.2f})."
            )

    st.subheader("AI Business Advisor")
    recommendations = generate_fallback_recommendations(kpis, categories, products, anomalies)
    for i, rec in enumerate(recommendations, start=1):
        st.write(f"**{i}. {rec}**")

    with st.expander("Show LLM-ready prompt"):
        st.code(build_recommendation_prompt(kpis, categories, products, anomalies))

except FileNotFoundError:
    st.error("Sample dataset not found.")
except Exception as exc:
    st.exception(exc)
