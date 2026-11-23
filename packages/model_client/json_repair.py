"""Robust JSON auto-repair engine for LLM outputs."""

import json
import re
from typing import Any, Dict


def repair_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans and repairs potentially malformed JSON emitted by LLMs:
    1. Extracts content from markdown code fences (```json ... ```).
    2. Strips leading/trailing conversational text.
    3. Removes invalid trailing commas before closing braces/brackets.
    4. Balances unclosed brackets and braces if truncated.
    5. Safely parses into a Python dictionary.
    """
    if not raw_text or not raw_text.strip():
        return {}

    text = raw_text.strip()

    # 1. Strip markdown fences if present
    fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
    match = fence_pattern.search(text)
    if match:
        text = match.group(1).strip()

    # 2. Find first '{' and last '}'
    start_idx = text.find("{")
    end_idx = text.rfind("}")

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx : end_idx + 1]
    elif start_idx != -1 and end_idx == -1:
        # Truncated JSON without closing brace
        text = text[start_idx:]

    # 3. Try standard parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # 4. Remove trailing commas before } or ]
    text = re.sub(r",\s*([\}\]])", r"\1", text)

    # 5. Fix common single quotes to double quotes for keys
    text = re.sub(r"(?<=\{|\,)\s*\'([a-zA-Z0-9_\-]+)\'\s*:", r'"\1":', text)

    # 6. Balance unclosed braces if response was truncated
    open_curly = text.count("{")
    close_curly = text.count("}")
    if open_curly > close_curly:
        text += "}" * (open_curly - close_curly)

    open_square = text.count("[")
    close_square = text.count("]")
    if open_square > close_square:
        text += "]" * (open_square - close_square)

    try:
        return json.loads(text)
    except Exception as exc:
        raise ValueError(f"Unable to parse or auto-repair JSON: {exc}. Cleaned string was: {text[:200]}")
