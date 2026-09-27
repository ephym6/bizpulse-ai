def generate_fallback_recommendations(kpis, categories, products, anomalies):
    """
    Deterministic fallback recommendations.
    Keeps the app useful even before an LLM is connected or if an API fails.
    """
    recommendations = []

    if kpis["profit_margin"] < 15:
        recommendations.append(
            "Review pricing and supplier costs because the overall profit margin is relatively low."
        )
    else:
        recommendations.append(
            "Protect your current margins while checking whether high-volume products can support small pricing experiments."
        )

    if not products.empty:
        top = products.iloc[0]
        recommendations.append(
            f"Keep {top['Product']} well stocked because it is currently the strongest revenue contributor."
        )

        low_margin = products.sort_values("Margin %").iloc[0]
        recommendations.append(
            f"Review {low_margin['Product']} because it has one of the lowest margins in the product mix."
        )

    if not anomalies.empty:
        recommendations.append(
            "Investigate the unusual revenue day(s) to identify possible stockouts, closures, promotions, or data-quality issues."
        )

    # Return exactly 3 concise items for the hackathon demo.
    return recommendations[:3]

def build_recommendation_prompt(kpis, categories, products, anomalies):
    category_text = categories.head(3).to_dict(orient="records")
    product_text = products.head(5).to_dict(orient="records")
    anomaly_text = anomalies[["Date", "Revenue", "z_score"]].to_dict(orient="records") if not anomalies.empty else []

    return f"""
You are BizPulse AI, a decision-support assistant for small business owners.

Use ONLY the verified metrics below. Do not invent financial values.
Give exactly 3 concise, practical recommendations. Explain why each action matters.
Avoid certainty language; these are recommendations for human review.

VERIFIED KPI SUMMARY:
{kpis}

TOP CATEGORIES:
{category_text}

TOP PRODUCTS:
{product_text}

ANOMALIES:
{anomaly_text}
""".strip()
