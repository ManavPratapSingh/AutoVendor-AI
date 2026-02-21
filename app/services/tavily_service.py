"""
Tavily Service — Scout Retrieval Layer.

Queries the lead URL via Tavily Search API to gather raw business intelligence:
company info, product pages, pricing, blog posts, testimonials.
"""

from tavily import TavilyClient
from app.config import get_settings


def run_tavily_research(lead_url: str) -> dict:
    """
    Execute a deep research query on the lead URL using Tavily.

    Args:
        lead_url: The target company's website URL.

    Returns:
        Raw Tavily search response as a dictionary.
    """
    settings = get_settings()
    client = TavilyClient(api_key=settings.tavily_api_key)

    # Primary search — company overview + products
    results = client.search(
        query=f"site:{lead_url} company overview products pricing integrations testimonials",
        search_depth="advanced",
        max_results=10,
        include_raw_content=True,
    )

    return results
