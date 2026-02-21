"""
Tests for Pipeline Orchestrator — end-to-end flow with mocked services.
"""

from unittest.mock import patch, MagicMock
from app.pipeline import generate_pitch
from app.schemas.request import PitchRequest, VendorProduct
from app.schemas.response import (
    ScoutOutput,
    CompanyProfile,
    StrategyOutput,
    AlignmentItem,
    PitchResponse,
    PitchContent,
)


# ── Fixtures ────────────────────────────────────────────────────────

MOCK_REQUEST = PitchRequest(
    lead_url="https://acme.com",
    vendor_product=VendorProduct(
        product_name="DataViz Pro",
        short_description="Real-time analytics dashboards",
        target_customer="Project management teams",
        core_features=["Live dashboards", "Custom reports"],
        unique_differentiator="AI-powered anomaly detection",
    ),
)

MOCK_TAVILY_DATA = {
    "results": [
        {"title": "Acme Corp", "url": "https://acme.com", "content": "Project management."}
    ]
}

MOCK_SCOUT = ScoutOutput(
    company_profile=CompanyProfile(
        company_name="Acme Corp",
        industry="Project Management",
        business_model="B2B SaaS",
        target_customers="Enterprise teams",
    ),
    pain_signals=["Manual reporting"],
    confidence_score=0.85,
)

MOCK_STRATEGY = StrategyOutput(
    opportunity_score=82,
    alignment_matrix=[
        AlignmentItem(
            vendor_feature="Live dashboards",
            lead_pain_signal="Manual reporting",
            alignment_score=0.9,
            reasoning="Direct match.",
        )
    ],
    recommended_pitch_angle="Replace manual reporting.",
    value_proposition="Cut reporting time by 80%.",
)

MOCK_PITCH = PitchResponse(
    pitch_id="test-uuid",
    pitch_html="<html><body>Pitch</body></html>",
    pdf_url="https://cdn.apitemplate.io/test.pdf",
    pitch_content=PitchContent(
        hero_headline="Acme Corp, Meet DataViz Pro",
        cta_text="Book a Demo",
    ),
)


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.pipeline.build_pitch_page")
@patch("app.pipeline.generate_strategy")
@patch("app.pipeline.extract_business_intelligence")
@patch("app.pipeline.run_tavily_research")
def test_generate_pitch_full_pipeline(
    mock_tavily, mock_scout, mock_strategist, mock_proposal
):
    """Should call all 4 layers in order and return a PitchResponse."""
    mock_tavily.return_value = MOCK_TAVILY_DATA
    mock_scout.return_value = MOCK_SCOUT
    mock_strategist.return_value = MOCK_STRATEGY
    mock_proposal.return_value = MOCK_PITCH

    result = generate_pitch(MOCK_REQUEST)

    # Verify each layer was called once
    mock_tavily.assert_called_once()
    actual_url = str(mock_tavily.call_args[0][0])
    assert actual_url == "https://acme.com/"
    mock_scout.assert_called_once_with(MOCK_TAVILY_DATA)
    mock_strategist.assert_called_once_with(MOCK_SCOUT, MOCK_REQUEST.vendor_product)
    mock_proposal.assert_called_once_with(
        MOCK_STRATEGY,
        MOCK_REQUEST.vendor_product,
        MOCK_SCOUT.company_profile,
    )

    # Verify result
    assert isinstance(result, PitchResponse)
    assert result.pitch_id == "test-uuid"
    assert result.pdf_url == "https://cdn.apitemplate.io/test.pdf"


@patch("app.pipeline.build_pitch_page")
@patch("app.pipeline.generate_strategy")
@patch("app.pipeline.extract_business_intelligence")
@patch("app.pipeline.run_tavily_research")
def test_generate_pitch_layer_ordering(
    mock_tavily, mock_scout, mock_strategist, mock_proposal
):
    """Should execute layers in the correct sequential order."""
    call_order = []

    mock_tavily.side_effect = lambda *a: (call_order.append("tavily"), MOCK_TAVILY_DATA)[1]
    mock_scout.side_effect = lambda *a: (call_order.append("scout"), MOCK_SCOUT)[1]
    mock_strategist.side_effect = lambda *a, **kw: (call_order.append("strategist"), MOCK_STRATEGY)[1]
    mock_proposal.side_effect = lambda *a, **kw: (call_order.append("proposal"), MOCK_PITCH)[1]

    generate_pitch(MOCK_REQUEST)

    assert call_order == ["tavily", "scout", "strategist", "proposal"]
