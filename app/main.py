"""
AutoVendor AI — FastAPI Application.

Main entry point with the /generate-pitch endpoint and health check.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.request import PitchRequest
from app.schemas.response import PitchResponse
from app.pipeline import generate_pitch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

app = FastAPI(
    title="AutoVendor AI",
    description="Transform a lead URL + vendor product info into a data-backed strategic pitch page.",
    version="0.1.0",
)

# CORS — allow all origins for V0
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/generate-pitch", response_model=PitchResponse)
def create_pitch(request: PitchRequest):
    """
    Generate a data-backed strategic pitch page.

    Pipeline:
        1. Tavily research on the lead URL
        2. Scout LLM extracts business intelligence
        3. Strategist LLM generates alignment analysis
        4. Proposal Generator builds HTML pitch + PDF

    Returns:
        PitchResponse with pitch_id, pitch_html, pdf_url, and structured content.
    """
    try:
        result = generate_pitch(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.getLogger(__name__).error("Pipeline failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}",
        )
