"""
Pipeline Orchestrator — wires all layers together.

Tavily (retrieval) → Scout LLM (extraction) → Strategist LLM (alignment) → Proposal Generator (pitch)
"""

import logging
from app.schemas.request import PitchRequest
from app.schemas.response import PitchResponse
from app.services.tavily_service import run_tavily_research
from app.services.scout_service import extract_business_intelligence
from app.services.strategist_service import generate_strategy
from app.services.proposal_service import build_pitch_page

logger = logging.getLogger(__name__)


def generate_pitch(request: PitchRequest) -> PitchResponse:
    """
    Execute the full AutoVendor AI pipeline.

    Flow:
        1. Tavily search on lead URL → raw web data
        2. Scout LLM extracts structured business intelligence
        3. Strategist LLM maps vendor features to lead pain signals
        4. Proposal Generator builds an HTML pitch page + PDF

    Args:
        request: PitchRequest with lead_url and vendor_product.

    Returns:
        PitchResponse with pitch_id, HTML content, PDF URL, and structured sections.

    Raises:
        Exception: Propagates errors from any layer with contextual logging.
    """
    lead_url = str(request.lead_url)

    # ── Layer 1: Tavily Research ────────────────────────────────────
    logger.info("🔍 Layer 1 — Running Tavily research on: %s", lead_url)
    tavily_data = run_tavily_research(lead_url)
    logger.info(
        "✅ Tavily returned %d results",
        len(tavily_data.get("results", [])),
    )

    # ── Layer 2: Scout LLM Extraction ──────────────────────────────
    logger.info("🧠 Layer 2 — Extracting business intelligence...")
    scout_output = extract_business_intelligence(tavily_data)
    logger.info(
        "✅ Scout extracted profile for: %s (confidence: %.2f)",
        scout_output.company_profile.company_name,
        scout_output.confidence_score,
    )

    # ── Layer 3: Strategist Alignment ──────────────────────────────
    logger.info("🎯 Layer 3 — Generating strategic alignment...")
    strategy_output = generate_strategy(scout_output, request.vendor_product)
    logger.info(
        "✅ Strategy complete — Opportunity Score: %d/100",
        strategy_output.opportunity_score,
    )

    # ── Layer 4: Proposal Generation ───────────────────────────────
    logger.info("📄 Layer 4 — Building pitch page...")
    pitch_response = build_pitch_page(
        strategy_output,
        request.vendor_product,
        scout_output.company_profile,
    )
    logger.info("✅ Pitch generated — ID: %s", pitch_response.pitch_id)

    if pitch_response.pdf_url:
        logger.info("📎 PDF available at: %s", pitch_response.pdf_url)
    else:
        logger.warning("⚠️ PDF generation was skipped or failed")

    return pitch_response
