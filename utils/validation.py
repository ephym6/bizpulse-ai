import pandas as pd

REQUIRED_COLUMNS = ['Date', 'Product', 'Category', 'Quantity', 'Selling Price', 'Cost Price']

def validate_sales_data(df):
    """
    Validates the uploaded sales CSV dataframe.
    Returns a tuple: (is_valid: bool, error_message: str)
    """
    # Check 1: Is the file completely empty?
    if df.empty:
        return False, "The uploaded file is empty. Please upload a file with sales records."
    
    # Check 2: Are any required columns missing?
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}. Please check your CSV format."
    
    # Check 3 (Optional but good): Ensure Quantity and Prices are numeric
    # We can add this later if we have time, but let's keep it simple for now.

    return True, "Data looks good!"