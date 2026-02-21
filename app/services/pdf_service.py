"""
PDF Service — HTML to PDF conversion via apitemplate.io.

Sends HTML content to the apitemplate.io API and returns
the CDN URL of the generated PDF document.
"""

import httpx
from app.config import get_settings

APITEMPLATE_CREATE_PDF_URL = "https://rest.apitemplate.io/v2/create-pdf"


def convert_html_to_pdf(html_content: str) -> str:
    """
    Convert HTML content to a PDF using apitemplate.io.

    Args:
        html_content: Complete HTML string to convert.

    Returns:
        CDN URL of the generated PDF.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status.
        ValueError: If the response does not contain a download URL.
    """
    settings = get_settings()

    response = httpx.post(
        APITEMPLATE_CREATE_PDF_URL,
        headers={
            "X-API-KEY": settings.apitemplate_api_key,
            "Content-Type": "application/json",
        },
        json={
            "body": html_content,
            "settings": {
                "paper_size": "A4",
                "orientation": "portrait",
                "margin_top": 20,
                "margin_bottom": 20,
                "margin_left": 20,
                "margin_right": 20,
            },
        },
        timeout=30.0,
    )

    response.raise_for_status()

    data = response.json()

    # apitemplate.io returns the PDF URL in the "download_url" field
    download_url = data.get("download_url") or data.get("url") or data.get("download")

    if not download_url:
        raise ValueError(f"No download URL in apitemplate.io response: {data}")

    return download_url
