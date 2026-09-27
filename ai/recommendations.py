import os
import json
import re
import pandas as pd
from typing import Union, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# FALLBACK RECOMMENDATIONS
# ============================================================

def generate_fallback_recommendations(
        kpis: Dict[str, Any] = None,
        categories: Union[pd.DataFrame, Dict, List] = None,
        products: Union[pd.DataFrame, Dict, List] = None,
        anomalies: Union[pd.DataFrame, List] = None
) -> List[str]:
    """
    Deterministic recommendations used when Gemini is unavailable.

    This keeps BizPulse functional even if:
    - the API key is missing
    - internet/API access fails
    - Gemini returns invalid output
    """

    kpis = kpis or {}
    recommendations = []

    # --------------------------------------------------------
    # 1. Profit margin recommendation
    # --------------------------------------------------------

    margin = float(kpis.get("profit_margin", 0) or 0)

    if margin < 15:
        recommendations.append(
            "Review supplier costs and pricing because the overall "
            "profit margin is relatively low."
        )
    else:
        recommendations.append(
            "Protect the current profit margin while testing whether "
            "high-demand products can support small pricing adjustments."
        )

    # --------------------------------------------------------
    # 2. Product recommendation
    # --------------------------------------------------------

    top_product = kpis.get("top_product")

    if top_product and top_product != "N/A":
        recommendations.append(
            f"Keep {top_product} well stocked because it is currently "
            "one of the strongest-performing products."
        )
    else:
        recommendations.append(
            "Monitor the highest-performing products closely and maintain "
            "sufficient stock to avoid losing potential sales."
        )

    # --------------------------------------------------------
    # 3. Anomaly recommendation
    # --------------------------------------------------------

    has_anomalies = False

    if isinstance(anomalies, pd.DataFrame):
        has_anomalies = not anomalies.empty

    elif isinstance(anomalies, list):
        has_anomalies = len(anomalies) > 0

    if has_anomalies:
        recommendations.append(
            "Investigate the unusual revenue period to determine whether "
            "it was caused by stockouts, closures, promotions, operational "
            "issues, or data-quality problems."
        )
    else:
        recommendations.append(
            "Continue monitoring revenue patterns and low-margin products "
            "to identify early signs of changing business performance."
        )

    return recommendations[:3]


# Backwards-compatible alias
get_fallback_recommendations = generate_fallback_recommendations


# ============================================================
# DATA SERIALIZATION
# ============================================================

def _dataframe_records(
        data: Any,
        limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame into JSON-safe records.

    reset_index() is important because analytics functions such as
    top_products() may store Product or Category in the DataFrame index.
    """

    if not isinstance(data, pd.DataFrame) or data.empty:
        return []

    safe = data.head(limit).reset_index()

    # Convert timestamps and NumPy values into JSON-safe forms
    records = []

    for record in safe.to_dict(orient="records"):
        cleaned = {}

        for key, value in record.items():

            if isinstance(value, pd.Timestamp):
                cleaned[key] = value.isoformat()

            elif hasattr(value, "item"):
                try:
                    cleaned[key] = value.item()
                except Exception:
                    cleaned[key] = str(value)

            else:
                cleaned[key] = value

        records.append(cleaned)

    return records


def _serialize_anomalies(
        anomalies: Any
) -> List[Dict[str, Any]]:
    """
    Convert anomaly results into a small JSON-safe structure.
    """

    if isinstance(anomalies, pd.DataFrame):

        if anomalies.empty:
            return []

        result = []

        for _, row in anomalies.head(5).iterrows():

            item = {
                "Date": str(row.get("Date", "")),
                "Revenue": float(row.get("Revenue", 0)),
            }

            if "z_score" in row:
                item["z_score"] = round(
                    float(row.get("z_score", 0)),
                    2
                )

            result.append(item)

        return result

    if isinstance(anomalies, list):
        return anomalies[:5]

    return []


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_recommendation_prompt(
        kpis,
        categories,
        products,
        anomalies
) -> str:
    """
    Build the Gemini prompt using only verified and aggregated
    BizPulse analytics.

    Raw customer-level information is not sent to the model.
    """

    category_data = _dataframe_records(
        categories,
        limit=3
    )

    product_data = _dataframe_records(
        products,
        limit=5
    )

    anomaly_data = _serialize_anomalies(
        anomalies
    )

    verified_data = {
        "kpis": kpis,
        "top_categories": category_data,
        "top_products": product_data,
        "anomalies": anomaly_data,
    }

    return f"""
You are BizPulse AI, a business decision-support assistant for
small and medium-sized business owners.

Your task is to convert VERIFIED business analytics into practical
business recommendations.

IMPORTANT RULES:

1. Use ONLY the verified information provided below.
2. Never invent revenue, profit, sales, margins, percentages,
   products, dates, or other financial figures.
3. Do not claim certainty about why an anomaly happened.
4. When discussing unusual activity, recommend investigation rather
   than assuming a cause.
5. Recommendations support human decision-making. They do not replace
   the business owner's judgment.
6. Keep recommendations concise and understandable to a non-technical
   small-business owner.
7. Give exactly THREE recommendations.
8. Each recommendation must describe an ACTION the owner can consider.
9. Do not mention that you are an AI model.
10. Return ONLY a JSON array containing exactly three strings.

VERIFIED BUSINESS DATA:

{json.dumps(verified_data, indent=2, default=str)}

Example response format:

[
  "Review...",
  "Consider...",
  "Investigate..."
]
""".strip()


# ============================================================
# GEMINI RESPONSE PARSING
# ============================================================

def _parse_recommendations(
        response_text: str
) -> List[str]:
    """
    Safely parse Gemini's response.

    Handles:
    - raw JSON
    - ```json code blocks
    - accidental surrounding text
    """

    if not response_text:
        return []

    text = response_text.strip()

    # Remove Markdown code fences if Gemini adds them
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # Try normal JSON first
    try:
        parsed = json.loads(text)

    except json.JSONDecodeError:

        # Try extracting the first JSON array from extra text
        match = re.search(
            r"\[[\s\S]*\]",
            text
        )

        if not match:
            return []

        try:
            parsed = json.loads(
                match.group(0)
            )

        except json.JSONDecodeError:
            return []

    if not isinstance(parsed, list):
        return []

    recommendations = []

    for item in parsed:

        if isinstance(item, str):

            cleaned = item.strip()

            if cleaned:
                recommendations.append(
                    cleaned
                )

    return recommendations[:3]


# ============================================================
# MAIN AI RECOMMENDATION FUNCTION
# ============================================================

def generate_recommendations(
        kpis: Dict[str, Any] = None,
        categories: Union[pd.DataFrame, List, Dict] = None,
        products: Union[pd.DataFrame, List, Dict] = None,
        anomalies: Union[pd.DataFrame, List] = None
) -> List[str]:
    """
    Generate three business recommendations using Gemini.

    If Gemini is unavailable for any reason, BizPulse automatically
    returns deterministic fallback recommendations instead.
    """

    kpis = kpis or {}

    if categories is None:
        categories = pd.DataFrame()

    if products is None:
        products = pd.DataFrame()

    if anomalies is None:
        anomalies = []

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    # Supports either name so your current .env does not have
    # to be changed immediately.
    api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("LLM_API_KEY")
    )

    if not api_key:
        return generate_fallback_recommendations(
            kpis,
            categories,
            products,
            anomalies
        )

    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    prompt = build_recommendation_prompt(
        kpis,
        categories,
        products,
        anomalies
    )

    try:

        # Import here so the dashboard can still start even if
        # google-genai is accidentally unavailable.
        from google import genai

        client = genai.Client(
            api_key=api_key
        )

        model_name = os.getenv(
            "LLM_MODEL",
            "gemini-2.5-flash"
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        recommendations = _parse_recommendations(
            response.text
        )

        # Require exactly 3 usable recommendations.
        if len(recommendations) == 3:
            return recommendations

        return generate_fallback_recommendations(
            kpis,
            categories,
            products,
            anomalies
        )

    except Exception as error:

        # Important for reliability:
        # AI failure must NEVER break the BizPulse dashboard.
        print(
            f"Gemini recommendation error: {error}"
        )

        return generate_fallback_recommendations(
            kpis,
            categories,
            products,
            anomalies
        )