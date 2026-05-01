"""AI Advisor module - wraps Task3 for portfolio advice."""

import sys
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

# Add Task3 to path
task3_path = Path(__file__).parent.parent / "Task3"
if str(task3_path) not in sys.path:
    sys.path.insert(0, str(task3_path))

from utils import log_warning, log_error


def build_prompt(portfolio: Dict[str, Any], metrics: Dict[str, Any], tone: str = "beginner") -> str:
    """Build prompt for LLM - similar to Task3's prompt_builder."""
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


def call_gemini(prompt: str) -> str:
    """Call Gemini API - wrapper around Task3's llm_client."""
    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(
            "google-generativeai not installed. Install with: pip install google-generativeai"
        ) from e
    
    api_key = __import__("os").environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    generation_config = genai.types.GenerationConfig(temperature=0.0)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt, generation_config=generation_config)
    
    return response.text


def parse_structured_output(text: str) -> Dict[str, Any]:
    """Parse JSON response from LLM."""
    import re
    
    # First attempt: direct JSON parse
    try:
        return json.loads(text)
    except Exception:
        pass
    
    # Extract JSON blob
    start = text.find("{")
    if start != -1:
        stack = []
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                stack.append(i)
            elif ch == "}":
                stack.pop()
                if not stack:
                    blob = text[start : i + 1]
                    try:
                        return json.loads(blob)
                    except Exception:
                        pass
    
    # Fallback: regex extraction
    kv = dict(re.findall(
        r'"?(summary|good_thing|improvement|verdict)"?\s*[:=]\s*"([^"]+)"',
        text,
        re.I
    ))
    if kv:
        return kv
    
    raise ValueError("Could not parse JSON from LLM response")


def get_ai_advice(
    portfolio: Mapping[str, Any],
    metrics: Dict[str, Any],
    tone: str = "beginner",
) -> Optional[Dict[str, Any]]:
    """
    Get AI advice for portfolio using Gemini LLM.
    
    Args:
        portfolio: Portfolio dictionary
        metrics: Risk metrics dictionary
        tone: Tone for advice (beginner, experienced, expert)
    
    Returns:
        Dict with advice or None if failed
    """
    try:
        prompt = build_prompt(dict(portfolio), metrics, tone)
        raw_response = call_gemini(prompt)
        
        parsed = parse_structured_output(raw_response)
        
        # Validate required fields
        required_fields = ["summary", "good_thing", "improvement", "verdict"]
        for field in required_fields:
            if field not in parsed:
                log_warning(f"Missing field '{field}' in LLM response, using default")
                parsed[field] = "N/A"
        
        return parsed
    
    except RuntimeError as e:
        log_error(f"LLM call failed: {e}")
        return None
    except ValueError as e:
        log_error(f"Failed to parse LLM response: {e}")
        return None
    except Exception as e:
        log_error(f"Unexpected error in AI advice: {e}")
        return None
