"""
core/config.py — configuration loader, saver, and live reload
"""
import os
import json

from core.paths import (
    CONFIG_PATH,
    APIS_PATH,
    KEYBINDS_PATH,
    THEMES_PATH,
    SANDBOX_DIR,
    CONFIG_DIR,
)

DEFAULT_CONFIG = {
    "api_key":             "",
    "model":               "",
    "url":                 "https://api.groq.com/openai/v1/chat/completions",
    "provider":            "",
    "max_loop":            20,
    "max_tokens":          700,
    "temperature":         0.2,
    "save_history":        True,
    "max_history_entries": 100,
    "max_session_turns":   40,
    "timeout":             60,
    "show_output":         True,
    "confirm_dangerous":   True,
    "working_dir":         SANDBOX_DIR,
    "theme":               "default",
    "stream":              False,
}

DEFAULT_KEYBINDS = {
    "clear":   "ctrl+l",
    "history": "ctrl+h",
    "help":    "ctrl+?",
    "exit":    "ctrl+c",
}

DEFAULT_THEMES = {
    "default": {
        "primary":   "96",
        "secondary": "95",
        "success":   "92",
        "error":     "91",
        "warning":   "93",
        "info":      "90",
        "user":      "94",
    },
    "dark": {
        "primary":   "36",
        "secondary": "35",
        "success":   "32",
        "error":     "31",
        "warning":   "33",
        "info":      "90",
        "user":      "34",
    },
    "matrix": {
        "primary":   "92",
        "secondary": "32",
        "success":   "92",
        "error":     "91",
        "warning":   "93",
        "info":      "32",
        "user":      "92",
    },
}


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg.update(saved)
        except Exception:
            pass
    return cfg


def save_config(cfg: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def load_apis() -> list:
    if not os.path.exists(APIS_PATH):
        return []
    try:
        with open(APIS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def load_keybinds() -> dict:
    if not os.path.exists(KEYBINDS_PATH):
        _write_defaults(KEYBINDS_PATH, DEFAULT_KEYBINDS)
        return DEFAULT_KEYBINDS.copy()
    try:
        with open(KEYBINDS_PATH, "r", encoding="utf-8") as f:
            kb = json.load(f)
        for k, v in DEFAULT_KEYBINDS.items():
            if k not in kb:
                kb[k] = v
        return kb
    except Exception:
        return DEFAULT_KEYBINDS.copy()


def load_themes() -> dict:
    if not os.path.exists(THEMES_PATH):
        _write_defaults(THEMES_PATH, DEFAULT_THEMES)
        return DEFAULT_THEMES.copy()
    try:
        with open(THEMES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_THEMES.copy()


def _write_defaults(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
