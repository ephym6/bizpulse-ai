import pandas as pd
from utils.validation import validate_sales_data, REQUIRED_COLUMNS

def test_valid_data():
    # Simulate a perfect CSV upload
    df = pd.DataFrame({
        'Date': ['2026-09-01'], 'Product': ['Milk'], 'Category': ['Dairy'],
        'Quantity': [5], 'Selling Price': [50], 'Cost Price': [40]
    })
    is_valid, msg = validate_sales_data(df)
    assert is_valid == True
    assert msg == "Data looks good!"

def test_empty_data():
    # Simulate an empty CSV upload
    df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    is_valid, msg = validate_sales_data(df)
    assert is_valid == False
    assert "empty" in msg.lower()

def test_missing_columns():
    # Simulate a CSV missing the 'Selling Price' column
    df = pd.DataFrame({
        'Date': ['2026-09-01'], 'Product': ['Milk'], 'Category': ['Dairy'],
        'Quantity': [5], 'Cost Price': [40]
    })
    is_valid, msg = validate_sales_data(df)
    assert is_valid == False
    assert "Missing required columns" in msg
    assert "Selling Price" in msg