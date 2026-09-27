import numpy as np
import pandas as pd

def detect_daily_revenue_anomalies(daily_revenue: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    """
    Simple, explainable anomaly detector using z-scores.
    Member 2 can later replace/extend this with Isolation Forest.
    """
    data = daily_revenue.copy()

    if len(data) < 3:
        data["z_score"] = 0.0
        return data.iloc[0:0]

    mean = data["Revenue"].mean()
    std = data["Revenue"].std(ddof=0)

    if std == 0 or np.isnan(std):
        data["z_score"] = 0.0
        return data.iloc[0:0]

    data["z_score"] = (data["Revenue"] - mean) / std
    return data[data["z_score"].abs() >= threshold].copy()
