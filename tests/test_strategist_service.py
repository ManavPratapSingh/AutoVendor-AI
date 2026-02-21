"""
Tests for Strategist Service — Alignment Engine.
"""

import json
from unittest.mock import patch, MagicMock
from app.services.strategist_service import generate_strategy
from app.schemas.request import VendorProduct
from app.schemas.response import ScoutOutput, CompanyProfile, StrategyOutput


# ── Fixtures ────────────────────────────────────────────────────────

MOCK_SCOUT_OUTPUT = ScoutOutput(
    company_profile=CompanyProfile(
        company_name="Acme Corp",
        industry="Project Management",
        business_model="B2B SaaS",
        target_customers="Enterprise teams",
    ),
    product_offerings=["Task management", "Gantt charts"],
    pricing_signals=["Enterprise pricing"],
    technology_signals=["REST API"],
    sales_process_indicators=["Demo booking"],
    pain_signals=["Manual reporting", "No real-time dashboards"],
    confidence_score=0.85,
)

MOCK_VENDOR_PRODUCT = VendorProduct(
    product_name="DataViz Pro",
    short_description="Real-time analytics dashboards",
    target_customer="Project management teams",
    core_features=["Live dashboards", "Custom reports", "API integration"],
    unique_differentiator="AI-powered anomaly detection",
)

MOCK_STRATEGY_LLM_RESPONSE = {
    "opportunity_score": 82,
    "alignment_matrix": [
        {
            "vendor_feature": "Live dashboards",
            "lead_pain_signal": "No real-time dashboards",
            "alignment_score": 0.95,
            "reasoning": "Direct feature-to-pain match.",
        },
        {
            "vendor_feature": "Custom reports",
            "lead_pain_signal": "Manual reporting",
            "alignment_score": 0.88,
            "reasoning": "Automates the manual reporting workflow.",
        },
    ],
    "strategic_gap_analysis": "No match for Gantt chart needs.",
    "recommended_pitch_angle": "Replace manual reporting with AI-powered real-time dashboards.",
    "value_proposition": "Cut reporting time by 80% with live dashboards built for project teams.",
}


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.services.strategist_service.anthropic.Anthropic")
@patch("app.services.strategist_service.get_settings")
def test_generate_strategy_returns_strategy_output(mock_settings, mock_anthropic_cls):
    """Should return a valid StrategyOutput from the LLM."""
    mock_settings.return_value.anthropic_api_key = "test-key"
    mock_settings.return_value.anthropic_model = "claude-sonnet-4-20250514"
    mock_settings.return_value.anthropic_temperature = 0.3

    mock_content_block = MagicMock()
    mock_content_block.text = json.dumps(MOCK_STRATEGY_LLM_RESPONSE)

    mock_response = MagicMock()
    mock_response.content = [mock_content_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    result = generate_strategy(MOCK_SCOUT_OUTPUT, MOCK_VENDOR_PRODUCT)

    assert isinstance(result, StrategyOutput)
    assert result.opportunity_score == 82
    assert len(result.alignment_matrix) == 2
    assert result.alignment_matrix[0].alignment_score == 0.95
    assert "manual reporting" in result.recommended_pitch_angle.lower()
    assert result.value_proposition != ""


@patch("app.services.strategist_service.anthropic.Anthropic")
@patch("app.services.strategist_service.get_settings")
def test_generate_strategy_passes_correct_data_to_llm(mock_settings, mock_anthropic_cls):
    """Should include both scout output and vendor info in the LLM prompt."""
    mock_settings.return_value.anthropic_api_key = "test-key"
    mock_settings.return_value.anthropic_model = "claude-sonnet-4-20250514"
    mock_settings.return_value.anthropic_temperature = 0.3

    mock_content_block = MagicMock()
    mock_content_block.text = json.dumps(MOCK_STRATEGY_LLM_RESPONSE)

    mock_response = MagicMock()
    mock_response.content = [mock_content_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    generate_strategy(MOCK_SCOUT_OUTPUT, MOCK_VENDOR_PRODUCT)

    call_args = mock_client.messages.create.call_args
    messages = call_args.kwargs["messages"]
    user_msg = messages[0]["content"]

    assert "Acme Corp" in user_msg
    assert "DataViz Pro" in user_msg
    assert "Live dashboards" in user_msg
