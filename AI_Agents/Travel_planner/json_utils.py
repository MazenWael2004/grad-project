"""
json_utils.py — shared helper for extracting JSON from LLM responses.

`extract_json_from_response` tries three strategies in order so the caller
never has to care about the exact output format.
"""

import json
import re


def extract_json_from_response(text: str) -> dict | None:
    
    if not text:
        return None

    text = text.strip()

    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  

    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue  # this '{' wasn't a JSON object start; keep scanning

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
