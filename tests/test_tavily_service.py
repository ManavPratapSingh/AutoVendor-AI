"""
Tests for Tavily Service — Scout Retrieval Layer.
"""

from unittest.mock import patch, MagicMock
from app.services.tavily_service import run_tavily_research


# ── Fixtures ────────────────────────────────────────────────────────

MOCK_TAVILY_RESPONSE = {
    "answer": "Stripe is a technology company that builds payment infrastructure.",
    "results": [
        {
            "title": "Stripe - Payment Processing Platform",
            "url": "https://stripe.com",
            "content": "Stripe powers online payments for internet businesses.",
            "raw_content": "Stripe is a financial infrastructure platform for businesses...",
        },
        {
            "title": "Stripe Pricing",
            "url": "https://stripe.com/pricing",
            "content": "2.9% + 30¢ per successful card charge.",
            "raw_content": "Integrated per-transaction pricing with no hidden fees...",
        },
    ],
}


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.services.tavily_service.TavilyClient")
@patch("app.services.tavily_service.get_settings")
def test_run_tavily_research_returns_results(mock_settings, mock_client_cls):
    """Should call Tavily client and return raw results."""
    mock_settings.return_value.tavily_api_key = "test-key"

    mock_client = MagicMock()
    mock_client.search.return_value = MOCK_TAVILY_RESPONSE
    mock_client_cls.return_value = mock_client

    result = run_tavily_research("https://stripe.com")

    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Stripe - Payment Processing Platform"

    mock_client.search.assert_called_once()
    call_kwargs = mock_client.search.call_args
    assert "advanced" in str(call_kwargs)


@patch("app.services.tavily_service.TavilyClient")
@patch("app.services.tavily_service.get_settings")
def test_run_tavily_research_uses_correct_api_key(mock_settings, mock_client_cls):
    """Should pass the API key from settings to the Tavily client."""
    mock_settings.return_value.tavily_api_key = "my-secret-key"

    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    mock_client_cls.return_value = mock_client

    run_tavily_research("https://example.com")

    mock_client_cls.assert_called_once_with(api_key="my-secret-key")


@patch("app.services.tavily_service.TavilyClient")
@patch("app.services.tavily_service.get_settings")
def test_run_tavily_research_empty_results(mock_settings, mock_client_cls):
    """Should handle empty results gracefully."""
    mock_settings.return_value.tavily_api_key = "test-key"

    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    mock_client_cls.return_value = mock_client

    result = run_tavily_research("https://unknown-site.com")

    assert result["results"] == []
