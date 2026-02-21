"""
Strategist Service — Alignment Engine.

Takes ScoutOutput + VendorProduct and uses an LLM (via OpenRouter) to generate
strategic alignment analysis: feature-to-pain mapping, opportunity scoring,
and pitch angle recommendation.
"""

import json
import re
from openai import OpenAI
from app.config import get_settings
from app.schemas.request import VendorProduct
from app.schemas.response import ScoutOutput, StrategyOutput

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

STRATEGIST_SYSTEM_PROMPT = """You are a strategic sales alignment expert. Your job is to analyze a lead company's profile and map a vendor's product features to the lead's pain signals to find the best sales opportunity.

You MUST respond with ONLY valid JSON (no markdown fences, no explanation) matching this exact schema:
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


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and extra text."""
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(text[brace_start : brace_end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM response: {text[:500]}")


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
    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=OPENROUTER_BASE_URL,
    )

    user_prompt = f"""## Lead Company Intelligence
{json.dumps(scout_output.model_dump(), indent=2)}

## Vendor Product Information
- Product Name: {vendor_product.product_name}
- Description: {vendor_product.short_description}
- Target Customer: {vendor_product.target_customer}
- Core Features: {', '.join(vendor_product.core_features)}
- Unique Differentiator: {vendor_product.unique_differentiator}

Analyze the alignment between this vendor's product and the lead company's needs. Map each vendor feature to the most relevant pain signal and generate a strategic recommendation."""

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        temperature=settings.openrouter_temperature,
        messages=[
            {"role": "system", "content": STRATEGIST_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_text = response.choices[0].message.content or ""
    raw_json = _extract_json(raw_text)
    return StrategyOutput(**raw_json)
