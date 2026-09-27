import pandas as pd
import pytest
from analytics.analytics import (
    load_and_clean,
    total_revenue,
    total_profit,
    profit_margin,
    total_quantity_sold,
    best_selling_product,
    highest_revenue_category
)

@pytest.fixture
def raw_sales_data():
    """Creates a mock dataframe with predictable outcomes for testing."""
    return pd.DataFrame({
        "Date": ["2026-09-01", "2026-09-01", "2026-09-02"],
        "Product": ["Milk", "Bread", "Milk"],
        "Category": ["Dairy", "Bakery", "Dairy"],
        "Quantity": [2, 6, 3], # Milk total: 5, Bread total: 6
        "Selling_Price": [100, 50, 100],
        "Cost_Price": [80, 30, 80]
    })

def test_load_and_clean(raw_sales_data):
    df = load_and_clean(raw_sales_data)
    
    # Verify new columns are created
    assert "Revenue" in df.columns
    assert "Profit" in df.columns
    assert "Profit_Margin" in df.columns
    
    # Verify math on the first row (2 Quantity * 100 Price = 200 Revenue)
    assert df.loc[0, "Revenue"] == 200
    # Verify profit (200 Rev - 160 Cost)
    assert df.loc[0, "Profit"] == 40

def test_core_calculations(raw_sales_data):
    df = load_and_clean(raw_sales_data)
    
    # Milk Rev: 500 (Profit 100) | Bread Rev: 300 (Profit 120) 
    # Expected Totals -> Rev: 800, Profit: 220, Qty: 11
    assert total_revenue(df) == 800.0
    assert total_profit(df) == 220.0
    assert total_quantity_sold(df) == 11
    
    # Bread sold 6, Milk sold 5
    assert best_selling_product(df) == "Bread"
    
    # Dairy Rev 500, Bakery Rev 300
    assert highest_revenue_category(df) == "Dairy"
    
    # Margin = 220 / 800 = 0.275
    assert profit_margin(df) == 0.275