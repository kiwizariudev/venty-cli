import os
import json
import datetime
from core.paths import NOTES_PATH, MEMORY_DIR

os.makedirs(MEMORY_DIR, exist_ok=True)

_SCHEMA = {"facts": [], "preferences": [], "projects": []}

def _load() -> dict:
    if not os.path.exists(NOTES_PATH):
        _save(_SCHEMA.copy())
        return _SCHEMA.copy()
    try:
        with open(NOTES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in _SCHEMA:
            if k not in data:
                data[k] = []
        return data
    except Exception:
        return _SCHEMA.copy()

def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def remember(text: str, category: str = "facts") -> str:
    data = _load()
    if category not in data:
        data[category] = []
    entry = {"text": text, "added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    data[category].append(entry)
    _save(data)
    return f"Remembered: {text}"

def forget(text: str) -> str:
    data = _load()
    removed = 0
    for cat in data:
        before = len(data[cat])
        data[cat] = [e for e in data[cat] if text.lower() not in e.get("text", "").lower()]
        removed += before - len(data[cat])
    _save(data)
    return f"Removed {removed} note(s) matching '{text}'"

def list_notes() -> str:
    data = _load()
    lines = []
    for cat, entries in data.items():
        if entries:
            lines.append(f"[{cat.upper()}]")
            for e in entries:
                lines.append(f"  • {e['text']}  ({e.get('added', '')})")
    return "\n".join(lines) if lines else "No notes saved yet."

def clear_notes() -> str:
    _save(_SCHEMA.copy())
    return "All notes cleared."

def get_memory_block() -> str:
    data = _load()
    lines = []
    for cat, entries in data.items():
        for e in entries:
            lines.append(f"  - [{cat}] {e['text']}")
    if not lines:
        return ""
    return "MEMORY (things the user told you to remember):\n" + "\n".join(lines)
