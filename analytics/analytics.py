import pandas as pd

def prepare_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean types and derive Revenue and Profit."""
    clean = df.copy()
    clean["Date"] = pd.to_datetime(clean["Date"])
    clean["Quantity"] = pd.to_numeric(clean["Quantity"], errors="raise")
    clean["Selling Price"] = pd.to_numeric(clean["Selling Price"], errors="raise")
    clean["Cost Price"] = pd.to_numeric(clean["Cost Price"], errors="raise")

    clean["Revenue"] = clean["Quantity"] * clean["Selling Price"]
    clean["Profit"] = clean["Quantity"] * (clean["Selling Price"] - clean["Cost Price"])
    return clean

def calculate_kpis(df: pd.DataFrame) -> dict:
    total_revenue = float(df["Revenue"].sum())
    total_profit = float(df["Profit"].sum())
    units_sold = float(df["Quantity"].sum())
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0.0

    product_revenue = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
    category_revenue = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "units_sold": units_sold,
        "profit_margin": profit_margin,
        "top_product": product_revenue.index[0] if not product_revenue.empty else "N/A",
        "top_category": category_revenue.index[0] if not category_revenue.empty else "N/A",
    }

def build_daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper for test suite expecting a DataFrame output."""
    return df.groupby(df["Date"].dt.date)["Revenue"].sum().reset_index()

def build_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
    )
    summary["Margin %"] = summary.apply(
        lambda row: (row["Profit"] / row["Revenue"] * 100) if row["Revenue"] else 0,
        axis=1,
    )
    return summary.sort_values("Revenue", ascending=False)

def build_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["Product", "Category"], as_index=False)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
    )
    summary["Margin %"] = summary.apply(
        lambda row: (row["Profit"] / row["Revenue"] * 100) if row["Revenue"] else 0,
        axis=1,
    )
    return summary.sort_values("Revenue", ascending=False)
