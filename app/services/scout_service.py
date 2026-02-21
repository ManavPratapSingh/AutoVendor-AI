"""
Scout Service — Structured Extraction Layer.

Takes raw Tavily search results and uses an LLM (via Groq) to extract
structured business intelligence as a ScoutOutput JSON object.
"""

import json
import re
from openai import OpenAI
from app.config import get_settings
from app.schemas.response import ScoutOutput

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SCOUT_SYSTEM_PROMPT = """You are a business intelligence analyst. Your job is to analyze raw web search results about a company and extract structured business intelligence.

You MUST respond with ONLY valid JSON (no markdown fences, no explanation) matching this exact schema:
{
  "company_profile": {
    "company_name": "string",
    "industry": "string",
    "business_model": "string",
    "target_customers": "string"
  },
  "product_offerings": ["string"],
  "pricing_signals": ["string"],
  "technology_signals": ["string"],
  "sales_process_indicators": ["string"],
  "pain_signals": ["string"],
  "confidence_score": 0.0
}

Rules:
- Extract ONLY factual information from the provided search results.
- "pain_signals" should capture challenges, bottlenecks, gaps, or areas where the company might need improvement.
- "confidence_score" should be between 0.0 and 1.0, reflecting how much reliable data you found.
- If a field cannot be determined, use an empty string or empty list.
- Do NOT fabricate information.
- Respond with ONLY the JSON object, nothing else."""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and extra text."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code fences
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first { ... } block
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(text[brace_start : brace_end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM response: {text[:500]}")


def extract_business_intelligence(tavily_results: dict) -> ScoutOutput:
    """
    Convert raw Tavily search results into structured business intelligence.

    Args:
        tavily_results: Raw response from Tavily search.

    Returns:
        ScoutOutput with structured company data.
    """
    settings = get_settings()
    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url=GROQ_BASE_URL,
    )

    # Build context from Tavily results
    search_context = _build_search_context(tavily_results)

    response = client.chat.completions.create(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SCOUT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Analyze the following search results and extract business intelligence:\n\n{search_context}",
            },
        ],
    )

    raw_text = response.choices[0].message.content or ""
    raw_json = _extract_json(raw_text)
    return ScoutOutput(**raw_json)


def _build_search_context(tavily_results: dict) -> str:
    """Format Tavily results into a readable text block for the LLM."""
    parts = []

    if "answer" in tavily_results and tavily_results["answer"]:
        parts.append(f"## Summary\n{tavily_results['answer']}\n")

    for i, result in enumerate(tavily_results.get("results", []), 1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")
        raw = result.get("raw_content", "")

        parts.append(f"### Source {i}: {title}")
        parts.append(f"URL: {url}")
        if content:
            parts.append(f"Snippet: {content}")
        if raw:
            # Truncate raw content to avoid token limits
            parts.append(f"Full Content: {raw[:2000]}")
        parts.append("")

    return "\n".join(parts)
