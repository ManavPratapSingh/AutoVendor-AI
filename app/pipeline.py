"""
Pipeline Orchestrator — AutoVendor AI.

Wires together all 4 layers:
1. Tavily Research
2. Scout Extraction (LLM)
3. Strategist Alignment (LLM)
4. Proposal Generation (LLM + PDF)
"""

import logging
from app.schemas.request import PitchRequest
from app.schemas.response import PitchResponse, ScoutOutput
from app.services.tavily_service import run_tavily_research
from app.services.scout_service import extract_business_intelligence
from app.services.strategist_service import generate_strategy
from app.services.proposal_service import build_pitch_page

logger = logging.getLogger("app.pipeline")
logging.basicConfig(level=logging.INFO)


def generate_pitch(request: PitchRequest) -> PitchResponse:
    """
    Execute the full 4-layer AI pipeline.

    Args:
        request: Lead URL + Vendor Product Info.

    Returns:
        Generated PitchResponse.
    """
    try:
        # Layer 1: Research
        logger.info(f"🔍 Layer 1 — Running Tavily research on: {request.lead_url}")
        tavily_data = run_tavily_research(request.lead_url)

        # Layer 2: Extraction
        logger.info("🧠 Layer 2 — Extracting business intelligence...")
        scout_output = extract_business_intelligence(tavily_data)
        logger.info(f"✅ Layer 2 Complete (Confidence: {scout_output.confidence_score})")

        # Layer 3: Strategic Alignment
        logger.info("⚡ Layer 3 — Generating strategic alignment...")
        strategy_output = generate_strategy(scout_output, request.vendor_product)
        logger.info(f"✅ Layer 3 Complete (Opportunity Score: {strategy_output.opportunity_score})")

        # Layer 4: Pitch Generation
        logger.info("🎨 Layer 4 — Generating pitch content and HTML...")
        pitch_response = build_pitch_page(
            strategy_output,
            request.vendor_product,
            scout_output.company_profile
        )
        logger.info(f"✅ Layer 4 Complete (Pitch ID: {pitch_response.pitch_id})")

        return pitch_response

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        raise e
