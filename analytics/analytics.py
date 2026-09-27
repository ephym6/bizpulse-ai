import pandas as pd
import numpy as np

# ---------------------------------------------------------------------
# 1. LOAD & CLEAN
# ---------------------------------------------------------------------

# Each standard field maps to a list of accepted raw-header variants.
# Matching is case-insensitive and ignores spaces/underscores/dashes,
# so "Selling Price", "selling_price", and "SellingPrice" all match.
COLUMN_ALIASES = {
    "Date": ["date", "saledate", "sale_date", "transactiondate", "orderdate"],
    "Product": ["product", "productid", "product_id", "productname", "item", "itemname", "sku"],
    "Category": ["category", "productcategory", "product_category", "itemcategory", "type"],
    "Quantity": ["quantity", "qty", "quantitysold", "quantity_sold", "unitssold", "units"],
    "Selling_Price": ["sellingprice", "selling_price", "unitprice", "unit_price", "price", "saleprice"],
    "Cost_Price": ["costprice", "cost_price", "unitcost", "unit_cost", "cost"],
    "Branch": ["branch", "region", "store", "location", "outlet"],
    "Payment_Method": ["paymentmethod", "payment_method", "payment"],
    "Discount": ["discount", "discountrate", "discount_rate", "discountpct"],
}

REQUIRED_FIELDS = ["Date", "Product", "Category", "Quantity", "Selling_Price", "Cost_Price"]
OPTIONAL_FIELDS = ["Branch", "Payment_Method", "Discount"]


def _normalize(name: str) -> str:
    """Lowercase and strip spaces/underscores/dashes for loose matching."""
    return str(name).lower().replace(" ", "").replace("_", "").replace("-", "")


def detect_columns(raw_columns) -> dict:
    """Match a CSV's raw column names to our standard schema.

    Returns {standard_name: raw_name} for every field that was found.
    Fields that can't be matched are simply absent from the result —
    callers decide what to do about missing required vs optional fields.
    """
    normalized_lookup = {_normalize(c): c for c in raw_columns}
    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            normalized_alias = _normalize(alias)

            if normalized_alias in normalized_lookup:
                detected[standard_name] = normalized_lookup[normalized_alias]
                break

    return detected


def load_and_clean(path: str) -> pd.DataFrame:
    """Load a sales CSV and return a clean, standardized dataframe.

    Works with any CSV whose columns roughly match a standard sales
    schema (date, product, category, quantity, price, cost) — column
    names don't need to match exactly. See COLUMN_ALIASES for the
    recognized variants. Raises a clear ValueError listing exactly
    which required fields couldn't be found, so the app can surface
    that to the user instead of failing silently.

    Any extra/unmatched columns from the source file (e.g. a
    'Sales_Amount' total, a sales rep name) are kept as-is, but Revenue
    is always computed fresh from Quantity * Selling_Price so a
    mismatched or unreliable total column can't silently break the
    numbers.
    """
    df = pd.read_csv(path)

    detected = detect_columns(df.columns)
    missing_required = [f for f in REQUIRED_FIELDS if f not in detected]
    if missing_required:
        raise ValueError(
            "This CSV is missing required column(s): "
            f"{', '.join(missing_required)}. "
            f"Found columns: {list(df.columns)}. "
            "Expected something like Date, Product, Category, Quantity, "
            "Selling Price, and Cost Price (naming can vary)."
        )

    # Rename only the columns we recognized; leave any extras untouched
    rename_map = {raw: standard for standard, raw in detected.items()}
    df = df.rename(columns=rename_map)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Drop rows with missing critical fields
    required = REQUIRED_FIELDS
    df = df.dropna(subset=required)

    # Type safety: coerce numeric columns, drop rows that fail
    if "Discount" in df.columns:
        df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)
    required_numeric = [
        "Quantity",
        "Selling_Price",
        "Cost_Price"
    ]

    # Convert first, then drop rows with invalid numeric values
    for col in required_numeric:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )
    # Remove values that could not be converted
    df = df.dropna(subset=required_numeric)

    # Then validate numeric ranges
    df = df[
        (df["Quantity"] > 0) &
        (df["Selling_Price"] >= 0) &
        (df["Cost_Price"] >= 0)
    ]

    # Recompute Revenue, Cost, Profit from source fields (not Sales_Amount)
    if "Discount" in df.columns:
        df["Discount"] = pd.to_numeric(
            df["Discount"], errors="coerce"
        ).fillna(0)

        # Support both:
        # 10  -> 10%
        # 0.10 -> 10%
        df.loc[df["Discount"] > 1, "Discount"] /= 100

        # Prevent invalid discount values
        df["Discount"] = df["Discount"].clip(0, 1)

        discount = df["Discount"]
    else:
        discount = 0

    # Recompute Revenue, Cost and Profit
    df["Revenue"] = (
            df["Quantity"]
            * df["Selling_Price"]
            * (1 - discount)
    )

    df["Cost"] = df["Quantity"] * df["Cost_Price"]
    df["Profit"] = df["Revenue"] - df["Cost"]

    df["Profit_Margin"] = np.where(
        df["Revenue"] > 0,
        df["Profit"] / df["Revenue"],
        0
    )

    df = df.sort_values("Date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------
# 2. CORE METRICS
# ---------------------------------------------------------------------

def total_revenue(df: pd.DataFrame) -> float:
    return round(df["Revenue"].sum(), 2)


def total_profit(df: pd.DataFrame) -> float:
    return round(df["Profit"].sum(), 2)


def profit_margin(df: pd.DataFrame) -> float:
    rev = df["Revenue"].sum()
    return round(df["Profit"].sum() / rev, 4) if rev > 0 else 0.0


def total_quantity_sold(df: pd.DataFrame) -> int:
    return int(df["Quantity"].sum())


def best_selling_product(df: pd.DataFrame) -> str:
    if df.empty:
        return "N/A"

    sales = df.groupby("Product")["Quantity"].sum()

    if sales.empty:
        return "N/A"

    return sales.idxmax()


def highest_revenue_category(df: pd.DataFrame) -> str:
    if df.empty:
        return "N/A"

    revenue = df.groupby("Category")["Revenue"].sum()

    if revenue.empty:
        return "N/A"

    return revenue.idxmax()


def daily_revenue(df: pd.DataFrame) -> pd.Series:
    return df.groupby(df["Date"].dt.date)["Revenue"].sum()


def weekly_revenue(df: pd.DataFrame) -> pd.Series:
    return df.groupby(pd.Grouper(key="Date", freq="W"))["Revenue"].sum()


def top_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    out = df.groupby("Product").agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Profit=("Profit", "sum"),
    ).sort_values("Revenue", ascending=False)
    return out.head(n)


def low_performing_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    out = df.groupby("Product").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
    ).sort_values("Revenue", ascending=True)
    return out.head(n)


def top_categories(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
    ).sort_values("Revenue", ascending=False)


def product_contribution(df: pd.DataFrame, n: int = 5) -> pd.Series:
    """% of total revenue each top product contributes."""
    rev_by_product = df.groupby("Product")["Revenue"].sum()

    total = rev_by_product.sum()

    if total <= 0:
        return pd.Series(dtype=float)

    contribution = (rev_by_product / total * 100).round(2)
    return contribution.sort_values(ascending=False).head(n)


def revenue_growth(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Period-over-period revenue growth (%) at weekly or monthly resolution."""
    series = df.groupby(pd.Grouper(key="Date", freq=freq))["Revenue"].sum()
    growth = series.pct_change().round(4) * 100
    return pd.DataFrame({"Revenue": series, "Growth_%": growth})


def weakest_day_of_week(df: pd.DataFrame) -> dict:
    """Identify which weekday underperforms vs the weekly average."""
    if df.empty:
        return {
            "day": "N/A",
            "pct_below_average": 0,
            "by_day": pd.Series(dtype=float)
        }

    daily = (
        df.groupby(df["Date"].dt.date)["Revenue"]
        .sum()
        .reset_index()
    )

    daily["Date"] = pd.to_datetime(daily["Date"])
    daily["Day"] = daily["Date"].dt.day_name()

    by_day = daily.groupby("Day")["Revenue"].mean()

    if by_day.empty:
        return {
            "day": "N/A",
            "pct_below_average": 0,
            "by_day": by_day
        }

    overall_avg = by_day.mean()
    weakest = by_day.idxmin()

    pct_below = (
        (overall_avg - by_day[weakest])
        / overall_avg
        * 100
        if overall_avg > 0
        else 0
    )

    return {
        "day": weakest,
        "pct_below_average": round(pct_below, 1),
        "by_day": by_day
    }

def calculate_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_revenue": total_revenue(df),
        "total_profit": total_profit(df),
        "profit_margin": profit_margin(df) * 100,
        "units_sold": total_quantity_sold(df),
        "top_product": best_selling_product(df),
        "top_category": highest_revenue_category(df),
    }

# ---------------------------------------------------------------------
# 3. TEST OUTPUT — proves the pipeline works end to end
# ---------------------------------------------------------------------

if __name__ == "__main__":
    df = load_and_clean("sales_data.csv")

    print("=" * 60)
    print("BizPulse AI — Analytics Engine Test Output")
    print("=" * 60)
    print(f"Rows loaded (clean): {len(df)}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}\n")

    print(f"Total Revenue:        KSh {total_revenue(df):,.2f}")
    print(f"Total Profit:         KSh {total_profit(df):,.2f}")
    print(f"Profit Margin:        {profit_margin(df) * 100:.1f}%")
    print(f"Total Units Sold:     {total_quantity_sold(df):,}")
    print(f"Best-Selling Product: {best_selling_product(df)}")
    print(f"Top Revenue Category: {highest_revenue_category(df)}\n")

    print("--- Top 5 Products by Revenue ---")
    print(top_products(df, 5), "\n")

    print("--- Category Performance ---")
    print(top_categories(df), "\n")

    print("--- Revenue Contribution (Top 5 Products) ---")
    print(product_contribution(df, 5), "\n")

    print("--- Weekly Revenue Growth (last 5 weeks) ---")
    print(revenue_growth(df, "W").tail(5), "\n")

    weak = weakest_day_of_week(df)
    print(f"--- Weakest Day: {weak['day']} ({weak['pct_below_average']}% below average) ---\n")

    print("Test output complete — all core metrics functions working.")
