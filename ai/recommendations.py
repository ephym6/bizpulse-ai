import os
import json
import pandas as pd
from typing import Union, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def generate_fallback_recommendations(
    kpis: Dict[str, Any] = None, 
    categories: Union[pd.DataFrame, Dict, List] = None, 
    products: Union[pd.DataFrame, Dict, List] = None, 
    anomalies: Union[pd.DataFrame, List] = None
) -> List[str]:
    """
    Deterministic fallback recommendations matching the original starter logic.
    """
    kpis = kpis or {"profit_margin": 20}
    recommendations = []

    # 1. Margin Check
    margin = kpis.get("profit_margin", 20)
    if margin < 15:
        recommendations.append("Review pricing and supplier costs because the overall profit margin is relatively low.")
    else:
        recommendations.append("Protect your current margins while checking whether high-volume products can support small pricing experiments.")

    # 2. Product Check
    if isinstance(products, pd.DataFrame) and not products.empty:
        top = products.iloc[0]
        prod_name = top.get('Product', 'top product')
        recommendations.append(f"Keep {prod_name} well stocked because it is currently the strongest revenue contributor.")
    elif isinstance(kpis, dict) and 'top_product' in kpis:
        recommendations.append(f"Keep {kpis['top_product']} well stocked because it is currently the strongest revenue contributor.")
    else:
        recommendations.append("Maintain sufficient stock levels for top-performing revenue contributors.")

    # 3. Anomaly Check
    has_anomalies = False
    if isinstance(anomalies, pd.DataFrame):
        has_anomalies = not anomalies.empty
    elif isinstance(anomalies, list):
        has_anomalies = len(anomalies) > 0

    if has_anomalies:
        recommendations.append("Investigate unusual revenue days to identify possible stockouts, closures, promotions, or data issues.")
    else:
        recommendations.append("Audit low-margin products and negotiate vendor terms or adjust pricing to improve overall profitability.")

    return recommendations[:3]


# Alias for backward compatibility
get_fallback_recommendations = generate_fallback_recommendations


def build_recommendation_prompt(kpis, categories, products, anomalies) -> str:
    """
    Starter prompt builder preserved for compatibility.
    """
    category_text = categories.head(3).to_dict(orient="records") if isinstance(categories, pd.DataFrame) else str(categories)
    product_text = products.head(5).to_dict(orient="records") if isinstance(products, pd.DataFrame) else str(products)
    anomaly_text = (
        anomalies[["Date", "Revenue", "z_score"]].to_dict(orient="records")
        if isinstance(anomalies, pd.DataFrame) and not anomalies.empty
        else str(anomalies)
    )

    return f"""
You are BizPulse AI, a decision-support assistant for small business owners.

Use ONLY the verified metrics below. Do not invent financial values.
Give exactly 3 concise, practical recommendations for human review.

VERIFIED KPI SUMMARY:
{kpis}

TOP CATEGORIES:
{category_text}

TOP PRODUCTS:
{product_text}

ANOMALIES:
{anomaly_text}

Return ONLY a raw JSON array of 3 actionable string recommendations, e.g., ["Rec 1", "Rec 2", "Rec 3"].
""".strip()


def generate_recommendations(
    kpis_or_insights: Union[Dict, Any] = None, 
    categories_or_anomalies: Union[pd.DataFrame, List, Any] = None, 
    products: Union[pd.DataFrame, Any] = None, 
    anomalies: Union[pd.DataFrame, List, Any] = None
) -> List[str]:
    """
    Flexible LLM recommendation generator.
    Supports both starter signature generate_recommendations(kpis, categories, products, anomalies)
    and custom signature generate_recommendations(insights, anomalies).
    """
    if products is None and anomalies is None:
        # Called as generate_recommendations(insights, anomalies)
        kpis = kpis_or_insights or {}
        cats = pd.DataFrame()
        prods = pd.DataFrame()
        anoms = categories_or_anomalies or []
    else:
        # Called with starter arguments (kpis, categories, products, anomalies)
        kpis = kpis_or_insights or {}
        cats = categories_or_anomalies if categories_or_anomalies is not None else pd.DataFrame()
        prods = products if products is not None else pd.DataFrame()
        anoms = anomalies if anomalies is not None else []

    api_key = os.getenv("LLM_API_KEY")
    if not api_key or api_key == "your_key_here":
        return generate_fallback_recommendations(kpis, cats, prods, anoms)

    prompt = build_recommendation_prompt(kpis, cats, prods, anoms)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        recs = json.loads(text)
        if isinstance(recs, list) and len(recs) > 0:
            return recs[:3]
        return generate_fallback_recommendations(kpis, cats, prods, anoms)

    except Exception:
        return generate_fallback_recommendations(kpis, cats, prods, anoms)