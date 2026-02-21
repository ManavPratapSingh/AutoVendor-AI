# 🧠 AutoVendor AI

> Transform a lead URL + vendor product info into a data-backed strategic pitch page.

## Architecture

```
Lead URL + Vendor Info
  → Tavily Search (Scout Retrieval)
  → Scout LLM (Structured Extraction)
  → Strategist LLM (Alignment Engine)
  → Proposal Generator (HTML Pitch + PDF)
```

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
copy .env.example .env
# Edit .env and add your API keys

# 4. Run the server
uvicorn app.main:app --reload
```

## API

### Health Check
```
GET /health
```

### Generate Pitch
```
POST /generate-pitch
Content-Type: application/json

{
  "lead_url": "https://example.com",
  "vendor_product": {
    "product_name": "Your Product",
    "short_description": "What it does",
    "target_customer": "Who it's for",
    "core_features": ["Feature 1", "Feature 2"],
    "unique_differentiator": "What makes it unique"
  }
}
```

**Response** includes `pitch_id`, `pitch_html`, `pdf_url`, and structured `pitch_content`.

## Run Tests

```bash
pytest tests/ -v
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TAVILY_API_KEY` | Tavily search API key |
| `OPENAI_API_KEY` | OpenAI API key (GPT-4) |
| `APITEMPLATE_API_KEY` | apitemplate.io PDF API key |
| `OPENAI_MODEL` | Model name (default: `gpt-4o`) |
| `OPENAI_TEMPERATURE` | Temperature (default: `0.3`) |
