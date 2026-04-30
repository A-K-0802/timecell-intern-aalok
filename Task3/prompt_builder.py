import json
from typing import Dict, Any
from config import DEFAULT_TONE


def build_prompt(portfolio: Dict[str, Any], metrics: Dict[str, Any], tone: str | None = None) -> str:
    tone = tone or DEFAULT_TONE
    payload = {
        "role": "financial_explainer",
        "audience": tone,
        "instructions": (
            "You are a helpful financial explainer for non-experts. "
            "Given the portfolio and precomputed risk metrics, produce a concise, non-jargon explanation. "
            "Output strictly valid JSON matching the schema: {summary, good_thing, improvement, verdict}. "
            "Verdict must be one of: Aggressive | Balanced | Conservative."
        ),
        "portfolio": portfolio,
        "metrics": metrics,
        "strict_json": True,
    }

    prompt = "Please follow the JSON-only output rules.\n" + json.dumps(payload, indent=2, default=str)
    return prompt
