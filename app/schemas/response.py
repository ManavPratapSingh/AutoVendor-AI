"""
Response schemas — output models for each pipeline layer.
"""

from pydantic import BaseModel
from typing import List, Optional


# ── Scout Layer Output ──────────────────────────────────────────────

class CompanyProfile(BaseModel):
    """Structured company profile extracted by the Scout LLM."""

    company_name: str = ""
    industry: str = ""
    business_model: str = ""
    target_customers: str = ""


class ScoutOutput(BaseModel):
    """Full output from the Scout LLM extraction layer."""

    company_profile: CompanyProfile = CompanyProfile()
    product_offerings: List[str] = []
    pricing_signals: List[str] = []
    technology_signals: List[str] = []
    sales_process_indicators: List[str] = []
    pain_signals: List[str] = []
    confidence_score: float = 0.0


# ── Strategist Layer Output ─────────────────────────────────────────

class AlignmentItem(BaseModel):
    """Single mapping of a vendor feature to a lead pain signal."""

    vendor_feature: str = ""
    lead_pain_signal: str = ""
    alignment_score: float = 0.0
    reasoning: str = ""


class StrategyOutput(BaseModel):
    """Full output from the Strategist reasoning layer."""

    opportunity_score: int = 0
    alignment_matrix: List[AlignmentItem] = []
    strategic_gap_analysis: str = ""
    recommended_pitch_angle: str = ""
    value_proposition: str = ""


# ── Proposal Generator Output ───────────────────────────────────────

class PitchContent(BaseModel):
    """Structured pitch content sections."""

    hero_headline: str = ""
    hero_subheadline: str = ""
    problem_framing: str = ""
    solution_positioning: str = ""
    quantified_benefits: List[str] = []
    social_proof: str = ""
    cta_text: str = ""
    cta_subtext: str = ""


class PitchResponse(BaseModel):
    """Final response from the Proposal Generator."""

    pitch_id: str = ""
    pitch_html: str = ""
    pdf_url: Optional[str] = None
    pitch_content: PitchContent = PitchContent()
