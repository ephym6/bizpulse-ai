import pandas as pd
from analytics.analytics import prepare_sales_data, calculate_kpis

def test_basic_kpis():
    df = pd.DataFrame([
        {
            "Date": "2026-09-01",
            "Product": "Milk",
            "Category": "Dairy",
            "Quantity": 2,
            "Selling Price": 100,
            "Cost Price": 60,
        }
    ])

    prepared = prepare_sales_data(df)
    kpis = calculate_kpis(prepared)

    assert kpis["total_revenue"] == 200
    assert kpis["total_profit"] == 80
    assert round(kpis["profit_margin"], 1) == 40.0
    assert kpis["top_product"] == "Milk"


def test_daily_revenue_groups_transactions_on_same_day():
    from analytics.analytics import build_daily_revenue

    df = pd.DataFrame([
        {"Date": "2026-09-01", "Product": "Milk", "Category": "Dairy", "Quantity": 2, "Selling Price": 100, "Cost Price": 60},
        {"Date": "2026-09-01", "Product": "Bread", "Category": "Bakery", "Quantity": 1, "Selling Price": 50, "Cost Price": 30},
    ])
    prepared = prepare_sales_data(df)
    daily = build_daily_revenue(prepared)
    assert len(daily) == 1
    assert daily.iloc[0]["Revenue"] == 250
