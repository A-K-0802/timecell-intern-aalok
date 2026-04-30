from pydantic import BaseModel, Field
from typing import List, Optional


class Asset(BaseModel):
    name: str
    allocation_pct: float = Field(..., ge=0, le=100)
    expected_crash_pct: float


class Portfolio(BaseModel):
    total_value_inr: float
    monthly_expenses_inr: float
    assets: List[Asset]


class ExplainerOutput(BaseModel):
    summary: str
    good_thing: str
    improvement: str
    verdict: str
