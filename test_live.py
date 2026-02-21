"""
Live production test — sends a real request to the /generate-pitch endpoint.
"""

import httpx
import json
import sys

payload = {
    "lead_url": "https://stripe.com",
    "vendor_product": {
        "product_name": "PayFlow Pro",
        "short_description": "AI-powered payment optimization platform",
        "target_customer": "SaaS companies processing online payments",
        "core_features": [
            "Smart payment routing",
            "AI fraud detection",
            "Revenue recovery automation",
            "Real-time analytics dashboard"
        ],
        "unique_differentiator": "ML-based payment success rate optimization that increases revenue by 5-15%"
    }
}

print("🚀 Sending request to /generate-pitch ...")
print(f"📋 Lead URL: {payload['lead_url']}")
print(f"📦 Product: {payload['vendor_product']['product_name']}")
print("-" * 60)

try:
    response = httpx.post(
        "http://127.0.0.1:8000/generate-pitch",
        json=payload,
        timeout=120.0,  # LLM calls can take a while
    )

    print(f"\n📡 Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pitch ID: {data.get('pitch_id', 'N/A')}")
        print(f"📎 PDF URL: {data.get('pdf_url', 'None')}")
        print(f"📄 HTML length: {len(data.get('pitch_html', ''))} chars")

        content = data.get("pitch_content", {})
        print(f"\n🎯 Hero: {content.get('hero_headline', 'N/A')}")
        print(f"   Sub:  {content.get('hero_subheadline', 'N/A')}")
        print(f"   CTA:  {content.get('cta_text', 'N/A')}")
        print(f"   Benefits: {content.get('quantified_benefits', [])}")

        # Save full response
        with open("test_live_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n💾 Full response saved to test_live_response.json")
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Request failed: {e}")
    sys.exit(1)
