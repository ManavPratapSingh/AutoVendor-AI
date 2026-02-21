"""
Tests for Scout Service — Structured Extraction Layer.
"""

import json
from unittest.mock import patch, MagicMock
from app.services.scout_service import extract_business_intelligence, _build_search_context
from app.schemas.response import ScoutOutput


# ── Fixtures ────────────────────────────────────────────────────────

MOCK_TAVILY_RESULTS = {
    "answer": "Acme Corp builds project management tools for enterprises.",
    "results": [
        {
            "title": "Acme Corp - Project Management",
            "url": "https://acme.com",
            "content": "Acme Corp helps enterprises manage complex projects.",
            "raw_content": "Founded in 2015, Acme Corp provides enterprise project management...",
        },
    ],
}

MOCK_SCOUT_LLM_RESPONSE = {
    "company_profile": {
        "company_name": "Acme Corp",
        "industry": "Project Management Software",
        "business_model": "B2B SaaS",
        "target_customers": "Enterprise teams",
    },
    "product_offerings": ["Task management", "Gantt charts", "Resource planning"],
    "pricing_signals": ["Enterprise pricing on request", "Free trial available"],
    "technology_signals": ["Cloud-native", "REST API", "SSO integration"],
    "sales_process_indicators": ["Demo booking", "Contact sales CTA"],
    "pain_signals": ["Manual reporting overhead", "Lack of real-time visibility"],
    "confidence_score": 0.85,
}


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.services.scout_service.OpenAI")
@patch("app.services.scout_service.get_settings")
def test_extract_business_intelligence_returns_scout_output(mock_settings, mock_openai_cls):
    """Should return a valid ScoutOutput parsed from the LLM response."""
    mock_settings.return_value.groq_api_key = "test-key"
    mock_settings.return_value.groq_model = "llama-3.3-70b-versatile"
    mock_settings.return_value.groq_temperature = 0.3

    mock_message = MagicMock()
    mock_message.content = json.dumps(MOCK_SCOUT_LLM_RESPONSE)

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    result = extract_business_intelligence(MOCK_TAVILY_RESULTS)

    assert isinstance(result, ScoutOutput)
    assert result.company_profile.company_name == "Acme Corp"
    assert result.company_profile.industry == "Project Management Software"
    assert result.confidence_score == 0.85
    assert "Manual reporting overhead" in result.pain_signals
    assert len(result.product_offerings) == 3


def test_build_search_context_formats_results():
    """Should format Tavily results into readable text."""
    context = _build_search_context(MOCK_TAVILY_RESULTS)

    assert "Acme Corp" in context
    assert "https://acme.com" in context
    assert "Summary" in context


def test_build_search_context_handles_empty_results():
    """Should handle empty Tavily results gracefully."""
    context = _build_search_context({"results": []})

    assert isinstance(context, str)
