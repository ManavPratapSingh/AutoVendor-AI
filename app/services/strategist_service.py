"""
Strategist Service — Alignment Engine.

Takes ScoutOutput + VendorProduct and uses Claude to generate strategic
alignment analysis: feature-to-pain mapping, opportunity scoring,
and pitch angle recommendation.
"""

import json
import anthropic
from app.config import get_settings
from app.schemas.request import VendorProduct
from app.schemas.response import ScoutOutput, StrategyOutput

STRATEGIST_SYSTEM_PROMPT = """You are a strategic sales alignment expert. Your job is to analyze a lead company's profile and map a vendor's product features to the lead's pain signals to find the best sales opportunity.

You MUST respond with ONLY valid JSON (no markdown, no explanation) matching this exact schema:
{
  "opportunity_score": 0,
  "alignment_matrix": [
    {
      "vendor_feature": "string",
      "lead_pain_signal": "string",
      "alignment_score": 0.0,
      "reasoning": "string"
    }
  ],
  "strategic_gap_analysis": "string",
  "recommended_pitch_angle": "string",
  "value_proposition": "string"
}

Rules:
- "opportunity_score" is 0-100, representing the overall sales opportunity strength.
- For each vendor feature, find the most relevant pain signal from the lead and score alignment (0.0-1.0).
- "strategic_gap_analysis" should identify where the vendor product does NOT align.
- "recommended_pitch_angle" should be a concise, actionable positioning statement.
- "value_proposition" should be a compelling one-liner the sales team can use.
- Be data-driven — base your analysis on the actual signals provided.
- Do NOT fabricate information.
- Respond with ONLY the JSON object, nothing else."""


def generate_strategy(scout_output: ScoutOutput, vendor_product: VendorProduct) -> StrategyOutput:
    """
    Generate strategic alignment analysis between lead and vendor.

    Args:
        scout_output: Structured intelligence about the lead company.
        vendor_product: Vendor's product information.

    Returns:
        StrategyOutput with opportunity scoring and alignment matrix.
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    user_prompt = f"""## Lead Company Intelligence
{json.dumps(scout_output.model_dump(), indent=2)}

## Vendor Product Information
- Product Name: {vendor_product.product_name}
- Description: {vendor_product.short_description}
- Target Customer: {vendor_product.target_customer}
- Core Features: {', '.join(vendor_product.core_features)}
- Unique Differentiator: {vendor_product.unique_differentiator}

Analyze the alignment between this vendor's product and the lead company's needs. Map each vendor feature to the most relevant pain signal and generate a strategic recommendation."""

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        temperature=settings.anthropic_temperature,
        system=STRATEGIST_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_text = response.content[0].text
    raw_json = json.loads(raw_text)
    return StrategyOutput(**raw_json)
