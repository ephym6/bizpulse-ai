import pandas as pd
import numpy as np
from typing import List, Dict, Any

def detect_daily_revenue_anomalies(daily_revenue: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    """
    Starter template function for daily revenue anomaly detection.
    Identifies abnormal daily revenue using Z-score thresholding.
    Returns a DataFrame containing anomaly rows to preserve app.py compatibility.
    """
    data = daily_revenue.copy()

    if data.empty or "Revenue" not in data.columns or len(data) < 3:
        if "Revenue" in data.columns:
            data["z_score"] = 0.0
        return data.iloc[0:0]

    mean = data["Revenue"].mean()
    std = data["Revenue"].std(ddof=0)

    if std == 0 or np.isnan(std):
        data["z_score"] = 0.0
        return data.iloc[0:0]

    data["z_score"] = (data["Revenue"] - mean) / std
    return data[data["z_score"].abs() >= threshold].copy()


def detect_anomalies(df: pd.DataFrame, date_col: str = 'Date', metric_col: str = 'Revenue', threshold: float = 2.0) -> List[Dict[str, Any]]:
    """
    Extended function returning structured dictionary alerts for LLM prompts or custom UI alerts.
    """
    if df.empty or metric_col not in df.columns:
        return []

    if date_col in df.columns:
        daily_data = df.groupby(date_col)[metric_col].sum().reset_index()
    else:
        daily_data = df.copy()

    mean = daily_data[metric_col].mean()
    std = daily_data[metric_col].std()

    if std == 0 or np.isnan(std):
        return []

    daily_data['z_score'] = (daily_data[metric_col] - mean) / std
    anomalies = daily_data[daily_data['z_score'].abs() >= threshold].copy()

    alerts = []
    for _, row in anomalies.iterrows():
        pct_diff = round(((row[metric_col] - mean) / mean) * 100, 1)
        direction = "drop" if pct_diff < 0 else "spike"
        
        alerts.append({
            "date": str(row[date_col]),
            "metric": metric_col,
            "value": round(float(row[metric_col]), 2),
            "expected_avg": round(float(mean), 2),
            "pct_change": pct_diff,
            "direction": direction,
            "message": f"Unusual revenue {direction} detected on {row[date_col]}. Revenue was {abs(pct_diff)}% {'below' if pct_diff < 0 else 'above'} normal daily average."
        })

    return alerts