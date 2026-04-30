import json
import re
from typing import Any, Dict, Optional

from models import ExplainerOutput


def _extract_first_json_blob(text: str) -> Optional[str]:
    # Try to find a balanced JSON object starting at the first '{'
    start = text.find("{")
    if start == -1:
        return None

    stack = []
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            stack.append(i)
        elif ch == "}":
            stack.pop()
            if not stack:
                return text[start : i + 1]
    return None


def parse_structured_output(text: str) -> Dict[str, Any]:
    # First attempt: direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Extract JSON-like blob
    blob = _extract_first_json_blob(text)
    if not blob:
        # Last attempt: try to find key:value pairs
        # fallback to minimal parsing via regex
        kv = dict(re.findall(r'"?(summary|good_thing|improvement|verdict)"?\s*[:=]\s*"([^"]+)"', text, re.I))
        if kv:
            return kv
        raise ValueError("No JSON found in LLM output")

    try:
        data = json.loads(blob)
    except Exception as exc:
        raise ValueError(f"Failed to parse JSON blob: {exc}\nBlob:\n{blob}") from exc

    # Validate/normalize with pydantic
    try:
        parsed = ExplainerOutput(**data)
        return parsed.dict()
    except Exception:
        # If validation fails, still return raw dict so caller can handle
        return data
