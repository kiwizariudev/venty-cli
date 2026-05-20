import os
import json
from core.paths import ALIASES_PATH, CONFIG_DIR

os.makedirs(CONFIG_DIR, exist_ok=True)

def load_aliases() -> dict:
    if not os.path.exists(ALIASES_PATH):
        return {}
    try:
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_aliases(aliases: dict) -> None:
    os.makedirs(os.path.dirname(ALIASES_PATH), exist_ok=True)
    try:
        with open(ALIASES_PATH, "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2)
    except Exception:
        pass

def set_alias(name: str, expansion: str) -> None:
    aliases = load_aliases()
    aliases[name] = expansion
    save_aliases(aliases)

def remove_alias(name: str) -> bool:
    aliases = load_aliases()
    if name in aliases:
        del aliases[name]
        save_aliases(aliases)
        return True
    return False

def resolve(user_input: str) -> str:
    aliases = load_aliases()
    for name, expansion in aliases.items():
        if user_input.lower().startswith(name.lower()):
            return expansion + user_input[len(name):]
    return user_input
