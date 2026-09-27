import pandas as pd

REQUIRED_COLUMNS = {
    "Date",
    "Product",
    "Category",
    "Quantity",
    "Selling Price",
    "Cost Price",
}

def validate_sales_data(df: pd.DataFrame):
    errors = []

    if df.empty:
        errors.append("The CSV is empty.")
        return False, errors

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")

    return len(errors) == 0, errors
