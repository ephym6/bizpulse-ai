import pandas as pd
import pytest
from analytics.analytics import prepare_sales_data, calculate_kpis

@pytest.fixture
def raw_sales_data():
    """Creates a mock dataframe with predictable outcomes for testing."""
    return pd.DataFrame({
        "Date": ["2026-09-01", "2026-09-01", "2026-09-02"],
        "Product": ["Milk", "Bread", "Milk"],
        "Category": ["Dairy", "Bakery", "Dairy"],
        "Quantity": [2, 6, 3],
        "Selling Price": [100, 50, 100],
        "Cost Price": [80, 30, 80]
    })

def test_prepare_and_calculate(raw_sales_data):
    # 1. Test data preparation
    df = prepare_sales_data(raw_sales_data)
    assert "Revenue" in df.columns
    assert "Profit" in df.columns
    
    # 2. Test the KPI dictionary output
    kpis = calculate_kpis(df)
    
    assert kpis["total_revenue"] == 800.0
    assert kpis["total_profit"] == 220.0
    assert kpis["units_sold"] == 11.0
    # Floating point math can be slightly imprecise, so we round it
    assert round(kpis["profit_margin"], 1) == 27.5
    assert kpis["top_product"] == "Milk"
    assert kpis["top_category"] == "Dairy"