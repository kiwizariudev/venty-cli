import os
import json
import datetime
from core.paths import HISTORY_PATH, CACHE_PATH, MEMORY_DIR, CACHE_DIR

os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def load_history() -> list:
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(session: list, max_entries: int = 100) -> None:
    try:
        existing = load_history()
        existing.extend(session)
        if len(existing) > max_entries:
            existing = existing[-max_entries:]
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def clear_history() -> None:
    if os.path.exists(HISTORY_PATH):
        os.remove(HISTORY_PATH)

def trim_session(session: list, max_turns: int) -> list:
    if len(session) <= max_turns * 2:
        return session
    return session[-(max_turns * 2):]

def log_action(action: str, args: list, success: bool, output=None) -> None:
    try:
        data = []
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        data.append({
            "timestamp":      datetime.datetime.now().isoformat(),
            "action":         action,
            "args":           args,
            "success":        success,
            "output_preview": str(output)[:120] if output else None,
        })
        data = data[-500:]
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def load_cache() -> list:
    if not os.path.exists(CACHE_PATH):
        return []
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def clear_cache() -> None:
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)

def get_stats() -> dict:
    data    = load_cache()
    total   = len(data)
    success = sum(1 for d in data if d.get("success"))
    counts: dict = {}
    for d in data:
        a = d.get("action", "?")
        counts[a] = counts.get(a, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total": total,
        "success": success,
        "top_actions": top
    }
