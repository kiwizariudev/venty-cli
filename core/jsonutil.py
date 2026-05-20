"""
core/jsonutil.py — robust JSON extraction from LLM responses.
"""
import re
import json


def extract_first_json(text: str) -> dict | None:
    """
    Extract the first valid JSON object from a response that may contain
    markdown fences, extra text, or multiple JSON blocks.
    """
    if not text:
        return None
    clean = re.sub(r"```json|```", "", text).strip()
    # try whole string
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    # find first {...} block (greedy from outermost brace)
    depth, start = 0, -1
    for i, ch in enumerate(clean):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    return json.loads(clean[start:i + 1])
                except json.JSONDecodeError:
                    start = -1
    return None
