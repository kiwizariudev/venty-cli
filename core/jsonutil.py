import json
import re

def extract_first_json(text: str) -> dict | None:
    if not text or not text.strip():
        return None

    clean = re.sub(r"```json|```", "", text).strip()

    try:
        obj = json.loads(clean)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass

    start = clean.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(clean)):
            ch = clean[i]
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = clean[start : i + 1]
                    try:
                        obj = json.loads(candidate)
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        break
        start = clean.find("{", start + 1)

    return None
