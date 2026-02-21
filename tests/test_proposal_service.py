"""
Tests for Proposal Service — Pitch Builder Layer.
"""

import json
from unittest.mock import patch, MagicMock
from app.services.proposal_service import build_pitch_page
from app.schemas.request import VendorProduct
from app.schemas.response import (
    CompanyProfile,
    StrategyOutput,
    AlignmentItem,
    PitchResponse,
)


# ── Fixtures ────────────────────────────────────────────────────────

MOCK_STRATEGY = StrategyOutput(
    opportunity_score=82,
    alignment_matrix=[
        AlignmentItem(
            vendor_feature="Live dashboards",
            lead_pain_signal="No real-time dashboards",
            alignment_score=0.95,
            reasoning="Direct match.",
        ),
    ],
    strategic_gap_analysis="No match for Gantt needs.",
    recommended_pitch_angle="Replace manual reporting with AI dashboards.",
    value_proposition="Cut reporting time by 80%.",
)

MOCK_VENDOR = VendorProduct(
    product_name="DataViz Pro",
    short_description="Real-time analytics dashboards",
    target_customer="Project management teams",
    core_features=["Live dashboards", "Custom reports"],
    unique_differentiator="AI-powered anomaly detection",
)

MOCK_COMPANY = CompanyProfile(
    company_name="Acme Corp",
    industry="Project Management",
    business_model="B2B SaaS",
    target_customers="Enterprise teams",
)

MOCK_PROPOSAL_LLM_RESPONSE = {
    "pitch_content": {
        "hero_headline": "Acme Corp, Meet Your New Analytics Engine",
        "hero_subheadline": "Real-time dashboards built for project teams.",
        "problem_framing": "Your team spends 15+ hours monthly on manual reports.",
        "solution_positioning": "DataViz Pro automates reporting with live dashboards.",
        "quantified_benefits": ["80% reduction in reporting time", "Real-time visibility"],
        "social_proof": "Trusted by 500+ project teams worldwide.",
        "cta_text": "Book a Demo",
        "cta_subtext": "See how DataViz Pro fits your workflow.",
    },
    "pitch_html": "<html><body><h1>Acme Corp Pitch</h1></body></html>",
}


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.services.proposal_service.convert_html_to_pdf")
@patch("app.services.proposal_service.OpenAI")
@patch("app.services.proposal_service.get_settings")
def test_build_pitch_page_returns_pitch_response(mock_settings, mock_openai_cls, mock_pdf):
    """Should return a valid PitchResponse with HTML content and structured sections."""
    mock_settings.return_value.groq_api_key = "test-key"
    mock_settings.return_value.groq_model = "llama-3.3-70b-versatile"

    mock_message = MagicMock()
    mock_message.content = json.dumps(MOCK_PROPOSAL_LLM_RESPONSE)

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    mock_pdf.return_value = "https://cdn.apitemplate.io/test.pdf"

    result = build_pitch_page(MOCK_STRATEGY, MOCK_VENDOR, MOCK_COMPANY)

    assert isinstance(result, PitchResponse)
    assert result.pitch_id != ""
    assert "<html>" in result.pitch_html
    assert result.pdf_url == "https://cdn.apitemplate.io/test.pdf"
    assert result.pitch_content.hero_headline == "Acme Corp, Meet Your New Analytics Engine"
    assert len(result.pitch_content.quantified_benefits) == 2


@patch("app.services.proposal_service.convert_html_to_pdf")
@patch("app.services.proposal_service.OpenAI")
@patch("app.services.proposal_service.get_settings")
def test_build_pitch_page_handles_pdf_failure(mock_settings, mock_openai_cls, mock_pdf):
    """Should still return a valid response even if PDF conversion fails."""
    mock_settings.return_value.groq_api_key = "test-key"
    mock_settings.return_value.groq_model = "llama-3.3-70b-versatile"

    mock_message = MagicMock()
    mock_message.content = json.dumps(MOCK_PROPOSAL_LLM_RESPONSE)

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    # Simulate PDF conversion failure
    mock_pdf.side_effect = Exception("API Template service unavailable")

    result = build_pitch_page(MOCK_STRATEGY, MOCK_VENDOR, MOCK_COMPANY)

    assert isinstance(result, PitchResponse)
    assert result.pitch_html != ""
    assert result.pdf_url is None
