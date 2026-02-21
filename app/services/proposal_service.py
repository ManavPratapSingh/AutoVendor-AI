"""
Proposal Service — Pitch Builder Layer.

Takes strategy output + vendor info + lead profile and uses Claude to
generate a complete pitch page as styled HTML content.
"""

import json
import uuid
import anthropic
from app.config import get_settings
from app.schemas.request import VendorProduct
from app.schemas.response import (
    CompanyProfile,
    StrategyOutput,
    PitchContent,
    PitchResponse,
)
from app.services.pdf_service import convert_html_to_pdf

PROPOSAL_SYSTEM_PROMPT = """You are a world-class sales copywriter and web designer. Your job is to generate a stunning, data-backed pitch page as complete HTML.

You MUST respond with ONLY valid JSON (no markdown, no explanation) matching this exact schema:
{
  "pitch_content": {
    "hero_headline": "string",
    "hero_subheadline": "string",
    "problem_framing": "string",
    "solution_positioning": "string",
    "quantified_benefits": ["string"],
    "social_proof": "string",
    "cta_text": "string",
    "cta_subtext": "string"
  },
  "pitch_html": "string"
}

Rules for pitch_html:
- Generate a COMPLETE, self-contained HTML document with inline CSS.
- Use a modern, premium design aesthetic: clean typography, professional color palette, generous whitespace.
- Include these sections: Hero, Problem, Solution, Benefits (quantified), Social Proof, CTA.
- Use the company name and specific data points from the strategy analysis.
- The HTML must be print-friendly and suitable for PDF conversion.
- Use Google Fonts (Inter or similar) via CDN link.
- Make it responsive and visually appealing.
- Do NOT use placeholder text — every element must be data-driven.

Rules for pitch_content:
- Extract the key content sections as structured data.
- hero_headline should be attention-grabbing and specific to the lead company.
- quantified_benefits should include specific numbers or percentages where possible.
- cta_text should be action-oriented.

Respond with ONLY the JSON object, nothing else."""


def build_pitch_page(
    strategy: StrategyOutput,
    vendor_product: VendorProduct,
    company_profile: CompanyProfile,
) -> PitchResponse:
    """
    Generate a complete HTML pitch page with structured content.

    Args:
        strategy: Strategic alignment analysis.
        vendor_product: Vendor's product information.
        company_profile: Lead company profile.

    Returns:
        PitchResponse with pitch_id, HTML content, PDF URL, and structured content.
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    pitch_id = str(uuid.uuid4())

    user_prompt = f"""## Lead Company
- Company: {company_profile.company_name}
- Industry: {company_profile.industry}
- Business Model: {company_profile.business_model}
- Target Customers: {company_profile.target_customers}

## Vendor Product
- Product: {vendor_product.product_name}
- Description: {vendor_product.short_description}
- Core Features: {', '.join(vendor_product.core_features)}
- Differentiator: {vendor_product.unique_differentiator}

## Strategic Analysis
- Opportunity Score: {strategy.opportunity_score}/100
- Recommended Pitch Angle: {strategy.recommended_pitch_angle}
- Value Proposition: {strategy.value_proposition}
- Gap Analysis: {strategy.strategic_gap_analysis}

## Alignment Matrix
{json.dumps([item.model_dump() for item in strategy.alignment_matrix], indent=2)}

Generate a compelling, data-backed pitch page for {company_profile.company_name} showcasing how {vendor_product.product_name} addresses their specific needs."""

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=8192,
        temperature=0.4,  # Slightly higher for creative copy
        system=PROPOSAL_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_text = response.content[0].text
    raw_json = json.loads(raw_text)

    pitch_html = raw_json.get("pitch_html", "")
    pitch_content_data = raw_json.get("pitch_content", {})

    # Convert HTML to PDF via apitemplate.io
    pdf_url = None
    try:
        if pitch_html:
            pdf_url = convert_html_to_pdf(pitch_html)
    except Exception:
        # PDF generation is non-critical — pitch still works without it
        pdf_url = None

    return PitchResponse(
        pitch_id=pitch_id,
        pitch_html=pitch_html,
        pdf_url=pdf_url,
        pitch_content=PitchContent(**pitch_content_data),
    )
