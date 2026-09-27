import pandas as pd
from utils.validation import validate_sales_data

def test_missing_column():
    df = pd.DataFrame([{"Date": "2026-09-01"}])
    valid, errors = validate_sales_data(df)
    assert not valid
    assert errors
