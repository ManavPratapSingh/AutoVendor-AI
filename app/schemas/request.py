"""
Request schemas — input models for the /generate-pitch endpoint.
"""

from pydantic import BaseModel, HttpUrl
from typing import List


class VendorProduct(BaseModel):
    """Vendor's product information provided by the user."""

    product_name: str
    short_description: str
    target_customer: str
    core_features: List[str]
    unique_differentiator: str


class PitchRequest(BaseModel):
    """Request body for POST /generate-pitch."""

    lead_url: HttpUrl
    vendor_product: VendorProduct
