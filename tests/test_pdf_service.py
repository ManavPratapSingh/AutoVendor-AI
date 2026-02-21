"""
Tests for PDF Service — HTML to PDF via apitemplate.io.
"""

from unittest.mock import patch, MagicMock
import pytest
from app.services.pdf_service import convert_html_to_pdf


# ── Fixtures ────────────────────────────────────────────────────────

SAMPLE_HTML = "<html><body><h1>Test Pitch</h1></body></html>"


# ── Tests ───────────────────────────────────────────────────────────

@patch("app.services.pdf_service.httpx.post")
@patch("app.services.pdf_service.get_settings")
def test_convert_html_to_pdf_success(mock_settings, mock_post):
    """Should return the download URL from apitemplate.io response."""
    mock_settings.return_value.apitemplate_api_key = "test-key"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "download_url": "https://cdn.apitemplate.io/generated/abc123.pdf"
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    url = convert_html_to_pdf(SAMPLE_HTML)

    assert url == "https://cdn.apitemplate.io/generated/abc123.pdf"
    mock_post.assert_called_once()

    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["headers"]["X-API-KEY"] == "test-key"
    assert call_kwargs.kwargs["json"]["body"] == SAMPLE_HTML


@patch("app.services.pdf_service.httpx.post")
@patch("app.services.pdf_service.get_settings")
def test_convert_html_to_pdf_no_download_url(mock_settings, mock_post):
    """Should raise ValueError if response has no download URL."""
    mock_settings.return_value.apitemplate_api_key = "test-key"

    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    with pytest.raises(ValueError, match="No download URL"):
        convert_html_to_pdf(SAMPLE_HTML)


@patch("app.services.pdf_service.httpx.post")
@patch("app.services.pdf_service.get_settings")
def test_convert_html_to_pdf_alternative_url_field(mock_settings, mock_post):
    """Should handle alternative URL field names from apitemplate.io."""
    mock_settings.return_value.apitemplate_api_key = "test-key"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "url": "https://cdn.apitemplate.io/generated/xyz789.pdf"
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    url = convert_html_to_pdf(SAMPLE_HTML)

    assert url == "https://cdn.apitemplate.io/generated/xyz789.pdf"


@patch("app.services.pdf_service.httpx.post")
@patch("app.services.pdf_service.get_settings")
def test_convert_html_to_pdf_sends_correct_settings(mock_settings, mock_post):
    """Should send A4 portrait settings to apitemplate.io."""
    mock_settings.return_value.apitemplate_api_key = "test-key"

    mock_response = MagicMock()
    mock_response.json.return_value = {"download_url": "https://example.com/file.pdf"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    convert_html_to_pdf(SAMPLE_HTML)

    call_kwargs = mock_post.call_args
    settings = call_kwargs.kwargs["json"]["settings"]
    assert settings["paper_size"] == "A4"
    assert settings["orientation"] == "portrait"
